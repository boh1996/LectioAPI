import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import team_elements as teamElementsApi

def importTeamElements ( school_id, branch_id, subject_id ):
	try:
		objectList = teamElementsApi.team_elements({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"subject_id" : subject_id
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
					"team_element_id" : str(row["team_element_id"]),
					"term" : objectList["term"]["value"]
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
					"team_element_id" : str(row["team_element_id"]),
					"school_id" : str(row["school_id"]),
					"branch_id" : str(row["branch_id"]),
					"subject_id" : str(subject_id),
					"type" : "team",
					"context_cards" : contextCards,
					"name" : unicode(str(row["name"]).decode("utf8")),
					"term" : str(objectList["term"]["value"])
				}

				status = sync.sync(db.team_elements, unique, element)

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