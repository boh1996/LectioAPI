import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import private_activity as privateActivityApi

def importPrivateActivity ( school_id, branch_id, student_id, activity_id, session = False, username = False, password = False ):
	try:
		objectList = privateActivityApi.private_activity({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"student_id" : student_id,
			"username" : username,
			"password" : password,
			"activity_id" : activity_id
		}, session)

		if objectList is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			row = objectList["appointment"]

			unique = {
				"activity_id" : str(activity_id),
				"type" : "private"
			}

			element = {
				"activity_id" : str(activity_id),
				"type" : "private",
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"student_id" : str(student_id),
				"title" : row["title"],
				"comment" : row["comment"],
				"start" : row["start"],
				"end" : row["end"]
			}

			status = sync.sync(db.events, unique, element)

			return True
		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
				db.events.remove({"activity_id" : str("activity_id")})
				return False
			elif "type" in objectList:
				error.log(__file__, False, objectList["type"])
				return False
			else:
				error.log(__file__, False, "Unknown error")

	except Exception, e:
		error.log(__file__, False, str(e))
		return False