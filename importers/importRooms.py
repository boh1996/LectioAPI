import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import rooms as roomsApi

def importRooms ( school_id, branch_id ):
	try:

		objectList = roomsApi.rooms({
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
			for row in objectList["rooms"]:
				unique = {
					"room_id" : row["room_id"]
				}

				element = {
					"room_id" : row["room_id"],
					"name" : row["name"],
					"number" : row["number"],
					"school_id" : row["school_id"],
					"branch_id" : row["branch_id"],
					"type" : row["type"]
				}

				status = sync.sync(db.rooms, unique, element)

				if sync.check_action_event(status) == True:
					for url in sync.find_listeners('room', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_general_listeners('room_general'):
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