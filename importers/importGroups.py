import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import groups as groupsApi

def importGroups ( school_id, branch_id ):
	try:
		objectList = groupsApi.groups({
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
			for row in objectList["groups"]:
				unique = {
					"group_id" : row["group_id"],
					"term" : objectList["term"]["value"]
				}

				element = {
					"group_id" : row["group_id"],
					"school_id" : row["school_id"],
					"branch_id" : row["branch_id"],
					"name" : row["name"],
					"type" : row["type"],
					"group_type" : row["group_type"],
					"term" : objectList["term"]["value"]

				}

				status = sync.sync(db.groups, unique, element)

				if sync.check_action_event(status) == True:
					for url in sync.find_listeners('group', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_general_listeners('group_general'):
						sync.send_event(url, status["action"], element)
			return True
		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
			else:
				error.log(__file__, False, "Unknown Error")

	except Exception, e:
		error.log(__file__, False, str(e))
		return False