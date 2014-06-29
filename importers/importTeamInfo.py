import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import team_info as teamInfoApi

def importTeamInfo ( school_id, branch_id, team_element_id, session = False, username = False, password = False ):
	try:
		objectList = teamInfoApi.team_info({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"team_element_id" : team_element_id,
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
			elementObject = objectList["information"]
			unique = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_element_id" : str(team_element_id)
			}

			element = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_element_id" : str(team_element_id),
				"team_id" : str(elementObject["team_id"])
			}

			status = sync.sync(db.team_elements, unique, element)

			unique = {
				"team_id" : str(elementObject["team_id"]),
				"school_id" : str(school_id),
				"branch_id" : str(branch_id)
			}

			element = {
				"team_id" : str(elementObject["team_id"]),
				"school_id" : str(school_id),
				"branch_id" : str(branch_id)
			}

			team_elements = []
			team_elements.append(status["_id"])

			existsing = db.teams.find(unique).limit(1)

			if existsing.count() > 0:
				existsing = existsing[0]

				if "team_elements" in existsing:
					if "team_elements" in existsing:
						for i in existsing["team_elements"]:
							if not i in team_elements:
								team_elements.append(i)

			element["team_elements"] = team_elements

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