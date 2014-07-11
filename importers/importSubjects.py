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
					"subject_id" : str(row["subject_id"]),
					"term" : objectList["term"]["value"]
				}

				element = {
					"subject_id" : str(row["subject_id"]),
					"abbrevation" : row["initial"],
					"name" : row["name"]
				}

				status = sync.sync(db.subjects, unique, element)

				unique = {
					"school_id" : str(row["school_id"]),
					"branch_id" : str(row["branch_id"]),
					"term" : objectList["term"]["value"],
					"subject_id" : str(row["subject_id"]),
					"type" : row["type"]
				}

				status = sync.sync(db.school_subjects, unique, unique)

				# Possible Connect with XPRS Subjects

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