import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import team_books as teamBooksApi

def importTeamBooks ( school_id, branch_id, team_id, session = False, username = False, password = False ):
	try:
		objectList = teamBooksApi.team_books({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"team_id" : team_id,
			"username" : username,
			"password" : password
		}, session)

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			for row in objectList["books"]:
				unique = {
					"title" : row["title"],
					"type" : row["type"]
				}

				element = {
					"title" : row["title"],
					"type" : row["type"]
				}

				status = sync.sync(db.books, unique, element)
				row["_id"] = status["_id"]
				del(row["team_id"])

			unique = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_id" : str(team_id)
			}

			element = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_id" : str(team_id),
				"books" : objectList["books"]
			}

			status = sync.sync(db.teams, unique, element)

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