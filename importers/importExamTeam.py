import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import exam_team as examTeamApi

def importExamTeam ( school_id, branch_id, test_team_id ):
	try:
		objectList = examTeamApi.exam_team({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"test_team_id" : test_team_id
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
				db.remove({"activity_id" : str("activity_id")})
				return False
			elif "type" in objectList:
				error.log(__file__, False, objectList["type"])
				return False
			else:
				error.log(__file__, False, "Unknown error")

	except Exception, e:
		error.log(__file__, False, str(e))
		return False

importExamTeam(517, 4733693427, 8703335625)