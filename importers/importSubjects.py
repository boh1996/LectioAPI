import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import subjects as subjectApi

def importSubjects ( school_id, branch_id ):
	try:

		objectList = subjectApi.subjects({
			"school_id" : school_id,
			"branch_id" : branch_id
		})

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			for row in objectList["subjects"]:
				unique = {
					"subject_id" : row["subject_id"],
					"term" : objectList["term"]["value"]
				}

				element = {
					"subject_id" : row["subject_id"],
					"school_id" : row["school_id"],
					"branch_id" : row["branch_id"],
					"term" : objectList["term"]["value"],
					"type" : row["type"],
					"initial" : row["initial"],
					"name" : row["name"],
					"type" : row["type"]
				}

				status = sync.sync(db.subjects, unique, element)

				if sync.check_action_event(status) == True:
					# Launch TeamElements scraper

					for url in sync.find_listeners('subject', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "subject", element)

					for url in sync.find_general_listeners('subject_general'):
						sync.send_event(url, status["action"], element)

			deleted = sync.find_deleted(db.rooms, {"school_id" : school_id, "branch_id" : branch_id, "term" : objectList["term"]["value"]}, ["subject_id"], objectList["subjects"])

			for element in deleted:subject
				for url in sync.find_listeners('subject', {"subject_id" : element["subject_id"]}):
					sync.send_event(url, 'deleted', element)

				for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
					sync.send_event(url, "subject_deleted", element)


			return True
		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
				return False
			else:
				error.log(__file__, False, "Unknown error")
				return False

	except Exception, e:
		error.log(__file__, False, str(e))
		return False