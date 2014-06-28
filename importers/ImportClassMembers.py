import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
from class_members import *

def importClassMembers ( school_id, branch_id, class_id, session = False, username = False, password = False ):
	try:
		objectList = class_members({
			"school_id" : school_id,
			"class_id" : class_id,
			"username" : username,
			"password" : password,
			"branch_id" : branch_id
		}, session)

		if objectList is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			members = []

			for row in objectList["students"]:
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

				# Add Field of Study
				element["field_of_study"] = {
					"name" : row["field_of_study"]["name"],
					"field_of_study_id" : row["field_of_study"]["field_of_study_id"]
				}

				if "picture_id" in row:
					# Launch Fetch Picture Task
					element["picture_id"] = row["picture_id"]

				status = sync.sync(db.persons, unique, element)

				members.append(status["_id"])

			for row in objectList["teachers"]:
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

				if "picture_id" in row:
					# Launch Fetch Picture Task
					element["picture_id"] = row["picture_id"]

				status = sync.sync(db.persons, unique, element)

				# Possible Teams Feature

				members.append(status["_id"])

			unique = {
				"class_id" : str(class_id)
			}

			element = {
				"members" : members,
				"class_id" : str(class_id),
				"school_id" : str(school_id),
				"branch_id" : str(branch_id)
			}

			status = sync.sync(db.classes, unique, element)

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