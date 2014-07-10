import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import activity_info as activityApi

def importActivityInfo ( school_id, branch_id, student_id, activity_id, username = False, password = False, session = False ):
	modules = None

	existing = db.schools.find({"school_id" : str(school_id)}).limit(1)

	if existing.count() > 0:
		existing = existing[0]
		if "module_info" in existing:
			modules = existing["module_info"]

	#try:
	objectList = activityApi.activity_info({
		"school_id" : school_id,
		"branch_id" : branch_id,
		"activity_id" : activity_id,
		"username" : username,
		"password" : password,
	}, activity_id, session, modules)

	if objectList is None:
			error.log(__file__, False, "Unknown Object")
			return False

	if not "status" in objectList:
		error.log(__file__, False, "Unknown Object")
		return False

	if objectList["status"] == "ok":
		row = objectList

		updated = row["updated"]

		existing = db.persons.find({"school_id" : str(school_id), "branch_id" : str(branch_id), "abbrevation" : updated["by"]})

		if existing.count() > 0:
			existing = existing[0]
			updated["_id"] = existing["_id"]

		created = row["created"]

		existing = db.persons.find({"school_id" : str(school_id), "branch_id" : str(branch_id), "abbrevation" : created["by"]})

		if existing.count() > 0:
			existing = existing[0]
			created["_id"] = existing["_id"]

		rooms = []
		classes = []
		students = []
		documents = []
		ressources = []
		teachers = []
		team_elements = []
		students_education_assigned = []

		for x in row["rooms"]:
			status = sync.sync(db.rooms, {"room_id" : x["room_id"]}, {"room_id" : x["room_id"], "school_id" : str(school_id), "branch_id" : str(branch_id)})

			rooms.append(status["_id"])

		for x in row["students"]:
			status = sync.sync(db.persons, {"student_id" : x["student_id"]}, {"student_id" : x["student_id"], "school_id" : str(school_id), "branch_id" : str(branch_id)})

			students.append(status["_id"])

			status = sync.sync(db.classes, {"class_id" : x["class_id"]}, {"class_id" : x["class_id"], "school_id" : str(school_id), "branch_id" : str(branch_id)})

			if not status["_id"] in classes:
				classes.append(status["_id"])

		for x in row["documents"]:
			element = {
				"document_id" : x["document_id"],
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"type" : x["type"],
				"size" : x["size"],
				"name" : x["name"]
			}

			status = sync.sync(db.documents, {"document_id" : x["document_id"]}, element)

			documents.append(status["_id"])

		for x in row["ressources"]:
			status = sync.sync(db.ressources, {"ressource_id" : x["ressource_id"]}, {"ressource_id" : x["ressource_id"]})

			ressources.append(status["_id"])

		for x in row["teachers"]:
			status = sync.sync(db.persons, {"teacher_id" : x["teacher_id"]}, {"teacher_id" : x["teacher_id"], "school_id" : str(school_id), "branch_id" : str(branch_id)})

			teachers.append(status["_id"])

		for x in row["students_education_assigned"]:
			status = sync.sync(db.persons, {"student_id" : x["student_id"]}, {"student_id" : x["student_id"], "school_id" : str(school_id), "branch_id" : str(branch_id)})

			students_education_assigned.append(status["_id"])

		for x in row["teams"]:
			status = sync.sync(db.team_elements, {"team_element_id" : x["team_id"]}, {"team_element_id" : x["team_id"], "school_id" : str(school_id), "branch_id" : str(branch_id), "name" : x["name"]})

			team_elements.append(status["_id"])

		unique = {
			"activity_id" : str(activity_id)
		}

		element = {
			"activity_id" : str(activity_id),
			"school_id" : str(school_id),
			"branch_id" : str(branch_id),
			"activity_status" : row["activity_status"],
			"event_type" : "school",
			"activity_type" : row["type"],
			"showed_at" : row["showed_at"],
			"updated" : updated,
			"created" : created,
			"students_resserved" : row["students_resserved"],
			"homework" : row["homework"],
			"links" : row["links"],
			"start" : row["date"]["start"],
			"end" : row["date"]["end"],
			"teachers" : teachers,
			"team_elements" : team_elements,
			"classes" : classes,
			"students" : students,
			"rooms" : rooms,
			"ressources" : ressources,
			"students_education_assigned" : students_education_assigned
		}

		if row["activity_status"] == "cancelled":
			element["status"] = "cancelled"

		if len(documents) > 0:
			element["documents"] = documents

		status = sync.sync(db.events, unique, element)

		return True
	else:
		if "error" in objectList:
			error.log(__file__, False, objectList["error"])
			return False
		else:
			error.log(__file__, False, "Unknown error")

	'''except Exception, e:
		error.log(__file__, False, str(e))
		return False'''

importActivityInfo(517, 4733693427, 4789793691, 8413179215, "boh1996", "jwn53yut", True)