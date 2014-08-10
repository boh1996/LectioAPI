import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import re
import sync
import exam_team as examTeamApi

def importExamTeam ( school_id, branch_id, test_team_id ):
	#try:
	objectList = examTeamApi.exam_team({
		"school_id" : school_id,
		"branch_id" : branch_id,
		"test_team_id" : test_team_id
	})

	if objectList is None:
		error.log(__file__, False, "Unknown Object")
		return False

	if not "status" in objectList:
		error.log(__file__, False, "Unknown Object")
		return False

	if objectList["status"] == "ok":
		row = objectList["information"]

		# Teachers
		teachers = []

		for x in row["teachers"]:
			existing = db.persons.find({"school_id" : str(school_id), "name" : x["name"], "branch_id" : str(branch_id), "abbrevation" : x["abbrevation"]})

			if existing.count() > 0:
				existing = existing[0]
				teachers.append({
					"name" : x["name"],
					"abbrevation" : x["abbrevation"],
					"_id" : existing["_id"]
				})
			else:
				teachers.append({
					"name" : x["name"],
					"abbrevation" : x["abbrevation"]
				})

		existing = db.schools.find({"school_id" : str(school_id), "branch_id" : str(branch_id)})[0]

		insitution_types = []

		if "insitution_types" in existing:
			insitution_types = existing["insitution_types"]

		if not row["gym_type"] in insitution_types:
			insitution_types.append(row["gym_type"])

		sync.sync(db.schools, {"school_id" : str(school_id), "branch_id" : str(branch_id)}, {"insitution_types" : insitution_types})

		# XPRS Subjects
		xprs = row["xprs"]

		existing = db.xprs_subjects.find({"code_full" : xprs["code_full"]})

		if existing.count() > 0:
			existing = existing[0]
			xprs["_id"] = existing["_id"]

			insitution_types = []
			test_name_codes = []
			test_types = []
			test_type_long_codes = []

			if "insitution_types" in existing:
				insitution_types = existing["insitution_types"]

			if "test_name_codes" in existing:
				test_name_codes = existing["test_name_codes"]

			if "test_types" in existing:
				test_types = existing["test_types"]

			if "test_type_long_codes" in existing:
				test_type_long_codes = existing["test_type_long_code"]

			if not row["gym_type"] in insitution_types:
				insitution_types.append(row["gym_type"])

			if not row["test_type_code"] in test_name_codes:
				test_name_codes.append(row["test_type_code"])

			if not row["xprs"]["xprs_type"] in test_types:
				test_types.append(row["xprs"]["xprs_type"])

			if not row["test_type_long_code"] in test_type_long_codes:
				test_type_long_codes.append(row["test_type_long_code"])

			element = {
				"insitution_types" : insitution_types,
				"test_name_codes" : test_name_codes,
				"test_types" : test_types,
				"test_type_long_codes" : test_type_long_codes
			}

			status = sync.sync(db.xprs_subjects, {"xprs_subject_id" : existing["xprs_subject_id"]}, element)

		censors = []

		# Censors - Connect With Insitutions Database when it arrives
		for x in row["censors"]:
			existing = db.schools.find({"$or" : [{"name" : re.compile("^" + x["institution"] + "$", re.IGNORECASE)}, {"institution" : x["institution"]}, {"institution_id" : x["institution_id"]}]})
			if existing.count() > 0:
				existing = existing[0]

				censors.append({
					"institution_id" : x["institution_id"],
					"institution" : x["institution"],
					"_id" : existing["_id"]
				})

				element = {
					"institution_id" : x["institution_id"],
					"institution" : x["institution"]
				}

				status = sync.sync(db.schools, {"school_id" : existing["school_id"]}, element)
			else:
				censors.append({
					"institution_id" : x["institution_id"],
					"institution" : x["institution"]
				})

		# Rooms
		rooms = []

		for x in row["rooms"]:
			data = {
				"alternative_name" : x["alternative_name"],
				"room_name" : x["room_name"],
				"exam_room_type" : x["exam_room_type"],
				"room_type" : x["room_type"]
			}

			existing = db.rooms.find({"name" : x["room_name"], "alternative_name" : x["alternative_name"]})

			if existing.count() > 0:
				data["_id"] = existing[0]["_id"]

			rooms.append(data)

		# Students
		students = []

		for x in row["students"]:
			data = {
				"student_class_id_full" : x["student_class_id_full"],
				"name" : x["name"],
				"in_group" : x["is_group"],
				"group_number" : x["group_number"],
				"group_time" : {
					"start" : x["group_time"]["start"],
					"end" : x["group_time"]["end"]
				},
				"examination" : {
					"start" : x["examination"]["start"],
					"end" : x["examination"]["end"]
				},
				"start" : x["start"],
				"end" : x["end"],
				"preperation_type" : x["preperation_type"],
				"preperation" : {
					"start" : x["preperation"]["start"],
					"end" : x["preperation"]["end"]
				},
				"class" : {
					"name" : x["class_name"],
					"code" : x["class_code"]
				}
			}

			classExisting = db.classes.find({"names.term" : row["term"]["value"], "names.name" : x["class_name"]})

			classObject = None

			if classExisting.count() > 0:
				classExisting = classExisting[0]
				classObject = classExisting

				data["class"]["_id"] = classExisting["_id"]

				status = sync.sync(db.classes, {"class_id" : classExisting["class_id"]}, {"name" : x["class_code"]})

			existing = db.persons.find({"$or" : [{"school_id" : str(school_id), "name" : x["name"], "class_student_id" : x["student_class_id_full"]}, {"school_id" : str(school_id), "name" : x["name"]}]})

			members = []

			if not classObject is None and "members" in classObject:
				for i in classObject["members"]:
					members.append(str(i))

			if existing.count() > 0:
				if not classObject is None and "members" in classObject:
					for match in existing:
						if str(match["_id"]) in members:
							data["_id"] = match["_id"]
				else:
					existing = existing[0]
					data["_id"] = existing["_id"]

			students.append(data)

		team = {
			"name" : row["team"]["team_class_name"],
			"team_name" : row["test_type_team_name"]
		}

		existing = db.team_elements.find({"name" : row["team"]["team_class_name"], "school_id" : str(school_id), "branch_id" : str(branch_id)})

		if existing.count() > 0:
			existing = existing[0]
			team["_id"] = existing["_id"]

			if "team_id" in existing:
				team["team_id"] = existing["team_id"]
				status = sync.sync(db.teams, {"team_id" : existing["team_id"]}, {"name" : row["test_type_team_name"]})

		# Connect With External Censor Event

		# Exam Team
		unique = {
			"test_team_id" : str(test_team_id),
			"type" : "exam"
		}


		element = {
			"test_team_id" : str(test_team_id),
			"type" : "exam",
			"school_id" : str(school_id),
			"branch_id" : str(branch_id),
			"test_type" : row["test_type"],
			"preperation_type" : row["preperation_type"],
			"start" : row["event"]["start"],
			"end" : row["event"]["end"],
			"exam" : {
				"start" : row["time"]["start"],
				"end" : row["time"]["end"]
			},
			"preperation" : {
				"start" : row["preperation"]["start"],
				"end" : row["preperation"]["end"]
			},
			"note" : row["note"],
			"test_team_name" : row["test_team_name"],
			"group_examination" : row["group_examination"],
			"test_type" : row["test_type"],
			"number_of_students" : row["number_of_students"],
			"test_type_long_code" : row["test_type_long_code"],
			"insitution_type" : row["gym_type"],
			"test_type_team_name" : row["test_type_team_name"],
			"test_type_code" : row["test_type_code"],
			"team_element" : team,
			"xprs_test" : row["xprs_test"],
			"xprs" : xprs,
			"teachers" : teachers,
			"censors" : censors,
			"rooms" : rooms,
			"students" : students
		}

		existing = db.subjects.find({"name" : xprs["subject"]})

		if existing.count() > 0:
			element["subject_id"] = existing[0]["subject_id"]

		status = sync.sync(db.events, unique, element)

		return True
	else:
		if "error" in objectList:
			error.log(__file__, False, objectList["error"])
			db.events.remove({"test_team_id" : str("test_team_id")})
			return False
		elif "type" in objectList:
			error.log(__file__, False, objectList["type"])
			return False
		else:
			error.log(__file__, False, "Unknown error")

	'''except Exception, e:
		error.log(__file__, False, str(e))
		return False'''

importExamTeam(517, 4733693427, 8703335618)