import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
from field_of_studies import *

def importFieldOfStudies ( school_id, branch_id, startYear ):
	try:
		objectList = field_of_studies({
			"school_id" : school_id,
			"branch_id" : branch_id
		}, startYear)

		if objectList is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":

			for row in objectList["list"]:
				unique = {
					"field_of_study_id" : str(row["field_of_study_id"])
				}

				contextCards = []
				contextCards.append(row["context_card_id"])
				existsing = db.field_of_studies.find(unique).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]
					if "context_cards" in existsing:
						for card in existsing["context_cards"]:
							if not card in contextCards:
								contextCards.append(card)

				element = {
					"study_direction_name" : unicode(str(row["study_direction_name"]).decode("utf8")),
					"gym_type" : unicode(str(row["gym_type"]).decode("utf8")),
					"start_year" : row["start_year"],
					"gym_type_short" :  unicode(str(row["gym_type_short"]).decode("utf8")),
					"field_of_study_id" : str(row["field_of_study_id"]),
					"school_id" : str(school_id),
					"branch_id" : str(branch_id),
					"name" : unicode(str(row["name"]).decode("utf8")),
					"context_cards" : contextCards,
					"main_subjects" : row["classes"]
				}

				# Classes Feature - Connection With XPRS Subjects
				# Launch Field Of Study Presentation Scraper
				status = sync.sync(db.field_of_studies, unique, element)

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