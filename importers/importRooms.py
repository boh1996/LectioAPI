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
					"room_id" : str(row["room_id"])
				}

				terms = []

				existsing = db.persons.find(unique).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]

					if "terms" in existsing:
						terms = existsing["terms"]

				if not objectList["term"]["value"] in terms:
					terms.append(objectList["term"]["value"])

				element = {
					"room_id" : str(row["room_id"]),
					"name" : row["name"],
					"alternative_name" : row["number"],
					"school_id" : str(row["school_id"]),
					"branch_id" : str(row["branch_id"]),
					"type" : row["type"],
					"terms" : terms
				}

				status = sync.sync(db.rooms, unique, element)

				'''if sync.check_action_event(status) == True:
					for url in sync.find_listeners('room', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "room", element)

					for url in sync.find_general_listeners('room_general'):
						sync.send_event(url, status["action"], element)'''

			'''deleted = sync.find_deleted(db.rooms, {"school_id" : school_id, "branch_id" : branch_id}, ["room_id"], objectList["rooms"])

			for element in deleted:
				for url in sync.find_listeners('room', {"room_id" : element["room_id"]}):
					sync.send_event(url, 'deleted', element)

				for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
					sync.send_event(url, "room_deleted", element)'''

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