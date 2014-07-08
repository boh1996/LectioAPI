import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import asignments as assignmentsApi
import assignment_info
import authenticate

def importAssignments ( school_id, branch_id, username, password, student_id ):
	try:
		objectList = assignmentsApi.assignments({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"student_id" : student_id,
			"username" : username,
			"password" : password
		})

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			row = objectList["information"]

			unique = {
				"exercise_id" : str(row["exercise_id"]),
				"student_id" : student_id
			}

			# Uploads
			uploads = []
			members = []
			documents = []
			availableStudents = []
			teachers = []

			element = {
				"exercise_id" : str(exercise_id),
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"student_id" : str(student_id),
				"team_element_name" : row["team"]["team_element_name"],
				"student_note" : row["student"]["student_note"],
				"grade_note" : row["student"]["grade_note"]
				"status" : row["student"]["status"],
				"grade" : row["student"]["grade"],
				"leave" : row["student"]["leave"],
				"finished" : row["student"]["finished"],
				"waiting_for" : row["student"]["waiting_for"],
				"uploads" : uploads,
				"members" : members,
				"documents" : documents,
				"group" : {
					"available_students" : availableStudents
				}
				"title" : row["title"],
				"date" : row["date"],
				"hours" : row["student_time"],
				"grading_scale" : row["grading_scale"],
				"note" : row["note"],
				"in_instruction_detail" : str(row["in_instruction_detail"]),
				"teachers" : teachers,
				"team_element_id" : str(row["team"]["team_element_id"]),
				"group_assignment" : str(row["group_assignment"])
			}

			status = sync.sync(db.assignments, unique, element)

			deleted = sync.find_deleted(db.assignments, {"student_id" : student_id}, ["exercise_id"], objectList["list"])

			return True
		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
				return False
			else:
				error.log(__file__, False, "Unknown error")

	except Exception, e:
		error.log(__file__, False, str(e))
		return False