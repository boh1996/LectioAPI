import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import grades as gradesApi

def importGrades ( school_id, branch_id, student_id, term, session = False, username = False, password = False ):
	try:
		objectList = gradesApi.grades({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"student_id" : student_id,
			"username" : username,
			"password" : password
		}, term, session)

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			diplomaLines = []

			for row in objectList["diploma"]:
				existsing = db.xprs_subjects.find({"name" : row["subject_name"], "level" : row["subject_level"]})

				if existsing.count() > 0:
					row["xprs_subject_id"] = existsing[0]["_id"]
					row["context_card_id"] = existsing[0]["context_card_id"]

				diplomaLines.append(row)

			existsing = db.persons.find({"student_id" : str(student_id)})

			unique = {
				"student_id" : str(student_id)
			}

			if existsing.count() > 0:
				element = existsing[0]
			else:
				element = {
					"student_id" : str(student_id)
				}

			if not "grades" in element:
				element["grades"] = {}

			if not "comments" in element["grades"]:
				element["grades"]["comments"] = {}

			if not "grades" in element["grades"]:
				element["grades"]["grades"] = {}

			if not "notes" in element["grades"]:
				element["grades"]["notes"] = {}

			element["grades"]["protocol_average"] = objectList["average"]
			element["grades"]["diploma"] = diplomaLines
			element["grades"]["protocol"] = objectList["protocol_lines"]
			element["grades"]["grades"][objectList["term"]["value"]] = objectList["grades"]
			element["grades"]["comments"][objectList["term"]["value"]] = objectList["comments"]
			element["grades"]["notes"][objectList["term"]["value"]] = objectList["grade_notes"]

			status = sync.sync(db.persons, unique, element)

		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
				return False
			else:
				error.log(__file__, False, "Unknown error")

	except Exception, e:
		error.log(__file__, False, str(e))
		return False