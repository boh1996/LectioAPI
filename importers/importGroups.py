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
					"team_element_id" : str(row["group_id"]),
					"term" : objectList["term"]["value"],
					"school_id" : str(row["school_id"]),
					"branch_id" : str(row["branch_id"])
				}

				contextCards = []
				contextCards.append(row["context_card_id"])
				existsing = db.team_elements.find(unique).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]
					if "context_cards" in existsing:
						for card in existsing["context_cards"]:
							if not card in contextCards:
								contextCards.append(card)

				element = {
					"team_element_id" : str(row["group_id"]),
					"school_id" : str(row["school_id"]),
					"branch_id" : str(row["branch_id"]),
					"name" : row["name"],
					"type" : row["type"],
					"group_type" : row["group_type"],
					"term" : objectList["term"]["value"],
					"type" : "group",
					"context_cards" : contextCards,
					"subject_id" : "1361688526"

				}

				status = sync.sync(db.team_elements, unique, element)

				# Launch Team Info Scraper

				'''if sync.check_action_event(status) == True:
					for url in sync.find_listeners('group', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "group", element)

					for url in sync.find_general_listeners('group_general'):
						sync.send_event(url, status["action"], element)'''

			#deleted = sync.find_deleted(db.groups, {"school_id" : school_id, "branch_id" : branch_id, "term" : objectList["term"]["value"], "type" : "group"}, ["group_id"], objectList["groups"])

			'''for element in deleted:
				for url in sync.find_listeners('group', {"group_id" : element["group_id"]}):
					sync.send_event(url, 'deleted', element)

				for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
					sync.send_event(url, "group_deleted", element)'''

			return True
		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
			else:
				error.log(__file__, False, "Unknown Error")

	except Exception, e:
		error.log(__file__, False, str(e))
		return False