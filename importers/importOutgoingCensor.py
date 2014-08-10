import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import re
import sync
import outgoing_censor as outgoingCensorApi

def importOutgoingCensor ( school_id, branch_id, outgoing_censor_id ):
	#try:
	objectList = outgoingCensorApi.outgoing_censor({
		"school_id" : school_id,
		"branch_id" : branch_id,
		"outgoing_censor_id" : outgoing_censor_id
	})

	if objectList is None:
		error.log(__file__, False, "Unknown Object")
		return False

	if not "status" in objectList:
		error.log(__file__, False, "Unknown Object")
		return False

	if objectList["status"] == "ok":
		row = objectList
		censor = {
			"name" : row["censor"]["name"],
			"abbrevation" : row["censor"]["abbrevation"]
		}

		existing = db.persons.find({"school_id" : str(school_id), "branch_id" : str(branch_id), "name" : censor["name"], "abbrevation" : censor["abbrevation"]})

		if existing.count() > 0:
			existing = existing[0]

			censor["_id"] = existing["_id"]

		institution = {
			"institution" : row["institution"]["name"],
			"institution_id" : row["institution"]["institution_id"]
		}

		# Institutions Link
		existing = db.schools.find({"$or" : [{"name" : re.compile("^" + institution["institution"] + "$", re.IGNORECASE)}, {"institution" : institution["institution"]}, {"institution_id" : institution["institution_id"]}]})
		if existing.count() > 0:
			existing = existing[0]

			institution["_id"] = existing["_id"]

			element = {
				"institution_id" : x["institution_id"],
				"institution" : x["institution"]
			}

			status = sync.sync(db.schools, {"school_id" : existing["school_id"]}, element)

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
				test_type_long_codes = existing["test_type_long_codes"]

			if not xprs["gym_type"] in insitution_types:
				insitution_types.append(xprs["gym_type"])

			if not xprs["test_type_code"] in test_name_codes:
				test_name_codes.append(xprs["test_type_code"])

			if not xprs["xprs_type"] in test_types:
				test_types.append(xprs["xprs_type"])

			if not xprs["test_type_long_code"] in test_type_long_codes:
				test_type_long_codes.append(xprs["test_type_long_code"])

			element = {
				"insitution_types" : insitution_types,
				"test_name_codes" : test_name_codes,
				"test_types" : test_types,
				"test_type_long_codes" : test_type_long_codes
			}

			status = sync.sync(db.xprs_subjects, {"xprs_subject_id" : existing["xprs_subject_id"]}, element)

		unique = {
			"outgoing_censor_id" : str(outgoing_censor_id)
		}

		element = {
			"outgoing_censor_id" : str(outgoing_censor_id),
			"branch_id" : str(branch_id),
			"school_id" : str(school_id),
			"censor" : censor,
			"note" : row["note"],
			"number_of_students" : row["number_of_students"],
			"test_type_team_name" : row["test_type_team_name"],
			"test_team" : row["test_team"],
			"institution" : institution,
			"period" : row["period"],
			"xprs" : xprs,
			"subject" : {
				"name" : xprs["subject"],
				"level" : xprs["level"]
			}
		}

		if row["description"] == True:
			element["subject"] = row["information"]["subject"]
			element["terms"] = row["information"]["terms"]
			element["institution"]["name"] = row["information"]["institution"]
			element["team_name"] = row["information"]["team_name"]

			existing = db.schools.find({"name" : re.compile(r".*" + element["institution"]["name"] + ".*")})

			if existing.count() > 0:
				existing = existing[0]
				element["institution"]["school_id"] = existing["school_id"]

				teachers = []

				team = db.teams.find({"school_id" : existing["school_id"], "name" : row["information"]["team_name"]})
				print row["information"]["team_name"]
				if team.count() > 0:
					print "Team Found!"
					teams = []
					team = team[0]

					element["team_id"] = team["team_id"]

					for x in row["information"]["teams"]:
						team_element = db.team_elements.find({"$or" : [{"team_id" : team["team_id"], "name" : x["name"]}, {"name" : x["name"], "school_id" :  existing["school_id"]}]})

						if team_element.count() > 0:
							team_element = team_element[0]

							teams.append({"name" : x["name"], "_id" : team_element["_id"]})
						else:
							teams.append(x)

					element["team_elements"] = teams

				else:
					element["team_elements"] = row["information"]["teams"]

				for x in row["information"]["teachers"]:
					teacher = db.persons.find({"name" : x["name"], "school_id" : existing["school_id"]})

					if teacher.count() > 0:
						teacher = teacher[0]

						teachers.append({"name" : x["name"], "_id" : teacher["_id"]})

					else:
						teachers.append({"name" : x["name"]})

				element["teachers"] = teachers

			else:
				element["team_elements"] = row["information"]["teams"]
				element["teachers"] = row["information"]["teachers"]

		sync.sync(db.events, unique, element)

		return True
	else:
		if "error" in objectList:
			error.log(__file__, False, objectList["error"])
			db.events.remove({"outgoing_censor_id" : str("outgoing_censor_id")})
			return False
		elif "type" in objectList:
			error.log(__file__, False, objectList["type"])
			return False
		else:
			error.log(__file__, False, "Unknown error")

	'''except Exception, e:
		error.log(__file__, False, str(e))
		return False'''

importOutgoingCensor(517, 4733693427, 9034801838)