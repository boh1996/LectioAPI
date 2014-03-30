import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import teams as teamsApi

def importTeams ( school_id, branch_id ):
	try:

		objectList = teamsApi.teams({
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
			for row in objectList["teams"]:
				unique = {
					"team_id" : row["team_id"],
					"term" : objectList["term"]["value"]
				}

				element = {
					"team_id" : row["team_id"],
					"school_id" : row["school_id"],
					"branch_id" : row["branch_id"],
					"term" : objectList["term"]["value"],
					"type" : row["type"],
					"initial" : row["initial"],
					"name" : row["name"],
					"type" : row["type"]
				}

				status = sync.sync(db.teams, unique, element)

				if sync.check_action_event(status) == True:
					for url in sync.find_listeners('team', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_general_listeners('team_general'):
						sync.send_event(url, status["action"], element)

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