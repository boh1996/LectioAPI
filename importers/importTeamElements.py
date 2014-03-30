import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import team_elements as teamElementsApi

def importTeamElements ( school_id, branch_id, team_id ):
	try:
		objectList = teamElementsApi.team_elements({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"team_id" : team_id
		})

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			for row in objectList["team_elements"]:
				unique = {
					"team_element_id" : row["team_element_id"],
					"term" : objectList["term"]["value"]
				}

				element = {
					"team_element_id" : row["team_element_id"],
					"school_id" : row["school_id"],
					"branch_id" : row["branch_id"],
					"term" : objectList["term"]["value"],
					"name" : row["name"]
				}

				status = sync.sync(db.team_elements, unique, element)

				if sync.check_action_event(status) == True:
					for url in sync.find_listeners('team_element', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "team_element", element)

					for url in sync.find_general_listeners('team_element_general'):
						sync.send_event(url, status["action"], element)

			deleted = sync.find_deleted(db.rooms, {"school_id" : school_id, "branch_id" : branch_id, "term" : objectList["term"]["value"]}, ["team_element_id"], objectList["team_elements"])

			for element in deleted:
				for url in sync.find_listeners('team_element', {"team_element_id" : element["team_element_id"]}):
					sync.send_event(url, 'deleted', element)

				for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
					sync.send_event(url, "team_element_deleted", element)


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