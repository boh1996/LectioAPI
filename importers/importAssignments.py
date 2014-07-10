import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import asignments as assignmentsfoApi
import authenticate

def importAssignment ( school_id, branch_id, student_id, exercise_id, session = False, username = False, password = False ):
	try:
		objectList = assignmentsfoApi.assignments({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"student_id" : student_id,
			"username" : username,
			"password" : password,
		}, session)

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			for row in objectList["list"]:

				team_elements = []

				unique = {
					"team_element_id" : row["team_element_id"]
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
					"team_element_id" : row["team_element_id"],
					"name" : row["group"],
					"context_cards" : contextCards
				}

				status = sync.sync(db.team_elements, unique, element)

				team_elements.append(status["_id"])

				unique = {
					"exercise_id" : str(row["exercise_id"]),
					"student_id" : student_id
				}

				element = {
					"exercise_id" : str(row["exercise_id"]),
					"school_id" : str(school_id),
					"branch_id" : str(branch_id),
					"student_id" : str(student_id),
					"week" : row["week"],
					"title" : row["title"],
					"date" : row["date"],
					"hours" : row["hours"],
					"status" : row["status"],
					"leave" : row["leave"],
					"waiting_for" : row["waiting_for"],
					"note" : row["note"],
					"grade" : row["grade"],
					"student_note" : row["student_note"],
					"team_elements" : team_elements
				}

				status = sync.sync(db.assignments, unique, element)

			return True
		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
				return False
			else:
				error.log(__file__, False, "Unknown error")

	except Exception, e:
		error.log(__file__, False, str(e))
		return False