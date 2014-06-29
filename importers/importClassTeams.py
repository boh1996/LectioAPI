import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import class_teams as classTeamsApi

def importClassTeams ( school_id, branch_id, class_id ):
	try:
		objectList = classTeamsApi.class_teams({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"class_id" : class_id
		})

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			teams = []

			for row in objectList["teams"]:
				unique = {
					"team_element_id" : str(row["team_element_id"]),
					"school_id" : str(school_id),
					"branch_id" : str(branch_id),
				}

				element = {
					"name" : row["name"],
					"team_element_id" : str(row["team_element_id"]),
					"school_id" : str(school_id),
					"branch_id" : str(branch_id),
				}

				status = sync.sync(db.team_elements, unique, element)

				teams.append(status["_id"])

			unique = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"class_id" : str(class_id)
			}

			element = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"class_id" : str(class_id),
				"teams" : teams
			}

			status = sync.sync(db.classes, unique, element)

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