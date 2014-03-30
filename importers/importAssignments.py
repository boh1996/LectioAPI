import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import asignments as assignmentsApi

def importAssignments ( school_id, branch_id, username, password, student_id ):
	#try:
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
		for row in objectList["list"]:
			unique = {
				"exercise_id" : row["exercise_id"],
				"student_id" : student_id
			}

			element = {
				"exercise_id" : row["exercise_id"],
				"school_id" : school_id,
				"branch_id" : branch_id,
				"student_id" : student_id,
				"week" : row["week"],
				"group" : row["group"],
				"title" : row["title"],
				"team_context_card_id" : row["context_card_id"],
				"link" : row["link"],
				"date" : row["date"],
				"hours" : row["hours"],
				"status" : row["status"],
				"leave" : row["leave"],
				"waiting_for" : row["waiting_for"],
				"note" : row["note"],
				"grade" : row["grade"],
				"student_note" : row["student_note"],
				"team_id" : row["team_id"]
			}

			status = sync.sync(db.assignments, unique, element)

			if sync.check_action_event(status) == True:
				for url in sync.find_listeners('assignment', unique):
					sync.send_event(url, status["action"], element)

				for url in sync.find_listeners('user', {"student_id" : student_id}):
					sync.send_event(url, "assignment", element)

		deleted = sync.find_deleted(db.assignments, {"student_id" : student_id}, ["exercise_id"], objectList["list"])

		for element in deleted:
			for url in sync.find_listeners('assignment', {"exercise_id" : element["exercise_id"]}):
				sync.send_event(url, 'deleted', element)

			for url in sync.find_listeners('user', {"student_id" : student_id}):
				sync.send_event(url, "assignment_deleted", element)

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

importAssignments(517, 4733693427 , "boh1996", "jwn53yut", 4789793691)