import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import context_card
import re

def importTeamElementInfo ( school_id, branch_id, team_element_id ):
	try:
		objectList = context_card.team({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"context_card_id" : "HE" + str(team_element_id)
		})

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			row = objectList["team"]
			unique = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_element_id" : str(team_element_id)
			}

			classes = []

			team_type = "other"

			for x in row["classes"]:
				team_type = "elective"
				current = db.classes.find({"class_id" : x["class_id"]}).limit(1)

				if current.count() > 0:
					current = current[0]
					if not current["_id"] in classes:
						classes.append(current["_id"])

			existsing = db.team_elements.find(unique).limit(1)

			if existsing.count() > 0:
				existsing = existsing[0]

				if "classes" in existsing:
					if "classes" in existsing:
						for i in existsing["classes"]:
							if not i in classes:
								classes.append(i)

				classProg = re.compile(r"(?P<class_name>.*) (?P<subject_abbrevation>.*)")
				classGroups = classProg.match(row["name"])

				if len(classes) == 0 and not classGroups is None:
					current = db.classes.find({"names.term" : existsing["term"], "names.name" : classGroups.group("class_name")}).limit(1)

					if current.count() > 0:
						team_type = "class_team"
						current = current[0]
						classes.append(current["_id"])

				if len(classes) == 1:
					team_type = "class_team"

			element = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_element_id" : str(team_element_id),
				"name" : row["name"],
				"subject_name" : row["subject"],
				"active" : str(row["active"]),
				"classes" : classes,
				"type" : row["type"],
				"team_type" : team_type
			}

			# Link with subject ID

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