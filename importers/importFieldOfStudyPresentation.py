import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
from field_of_study_presentation import *

def importFieldOfStudyPresentation ( school_id, branch_id, field_of_study_id ):
	try:
		objectList = field_of_study({
			"school_id" : school_id,
			"branch_id" : branch_id
		}, field_of_study_id)

		if objectList is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			unique = {
				"field_of_study_id" : str(field_of_study_id)
			}

			contextCards = []
			contextCards.append("SR" + str(field_of_study_id))
			existsing = db.field_of_studies.find(unique).limit(1)

			if existsing.count() > 0:
				existsing = existsing[0]
				if "context_cards" in existsing:
					for card in existsing["context_cards"]:
						if not card in contextCards:
							contextCards.append(card)

			element = {
				"years" : objectList["years"],
				"semesters" : objectList["semesters"],
				"presentation" : objectList["presentation"],
				"subject_types" : objectList["subject_types"],
				"elective_groups" : objectList["elective_groups"],
				"subjects" : objectList["subjects"],
				"field_of_study_id" : str(field_of_study_id),
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"context_cards" : contextCards
			}

			# Link with XPRS Subjects
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