import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import group_members as groupMembersApi

def importGroupMembers ( school_id, branch_id, team_element_id, session = False, username = False, password = False ):
	try:
		objectList = groupMembersApi.group_members({
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
			members = []

			for row in objectList["objects"]:
				if row["type"] == "student":
					unique = {
						"student_id" : row["person_id"]
					}

					contextCards = []
					contextCards.append(row["context_card_id"])
					existsing = db.persons.find(unique).limit(1)

					if existsing.count() > 0:
						existsing = existsing[0]
						if "context_cards" in existsing:
							for card in existsing["context_cards"]:
								if not card in contextCards:
									contextCards.append(card)

					element = {
						"type" : "student",
						"student_id" : row["person_id"],
						"name" : unicode(str(row["full_name"]).decode("utf8")),
						"class_student_id" : unicode(str(row["person_text_id"]).decode("utf8")),
						"last_name" : unicode(str(row["last_name"]).decode("utf8")),
						"first_name" : unicode(str(row["first_name"]).decode("utf8")),
						"context_cards" : contextCards,
						"school_id" : str(school_id),
						"branch_id" : str(branch_id)
					}

					if "field_of_study" in row:
						# Add Field of Study Sybc
						element["field_of_study"] = {
							"name" : row["field_of_study"]["name"],
							"field_of_study_id" : row["field_of_study"]["field_of_study_id"]
						}

					if "picture_id" in row:
						# Launch Fetch Picture Task
						element["picture_id"] = row["picture_id"]
				else:
					unique = {
						"teacher_id" : row["person_id"]
					}

					contextCards = []
					contextCards.append(row["context_card_id"])
					existsing = db.persons.find(unique).limit(1)

					if existsing.count() > 0:
						existsing = existsing[0]
						if "context_cards" in existsing:
							for card in existsing["context_cards"]:
								if not card in contextCards:
									contextCards.append(card)

					element = {
						"teacher_id" : str(row["person_id"]),
						"last_name" : unicode(str(row["last_name"]).decode("utf8")),
						"first_name" : unicode(str(row["first_name"]).decode("utf8")),
						"type" : "teacher",
						"name" : unicode(str(row["full_name"]).decode("utf8")),
						"abbrevation" : unicode(str(row["person_text_id"]).decode("utf8")),
						"context_cards" : contextCards,
						"school_id" : str(school_id),
						"branch_id" : str(branch_id)
					}

					# Add Team to teacher

				if "picture_id" in row:
					# Launch Fetch Picture Task
					element["picture_id"] = row["picture_id"]

				status = sync.sync(db.persons, unique, element)

				members.append(status["_id"])

			unique = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_element_id" : str(team_element_id)
			}

			element = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_element_id" : str(team_element_id),
				"members" : members
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