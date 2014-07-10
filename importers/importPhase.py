import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import phase as phaseApi

def importPhase ( school_id, branch_id, phase_id, session = False, username = False, password = False ):
	try:
		objectList = phaseApi.phase({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"phase_id" : phase_id,
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
			row = objectList["phase"]

			activities = []

			for x in row["activities"]:
				unique = {
					"activity_id" : x["activity_id"]
				}

				element = {
					"activity_id" : x["activity_id"],
					"school_id" : str(school_id),
					"branch_id" : str(branch_id)
				}

				status = sync.sync(db.events, unique, element)

				activities.append(status["_id"])

				# Launch Activity scraper

			unique = {
				"phase_id" : str(phase_id)
			}

			team_elements = []

			for x in row["teams"]:
				existsing = db.team_elements.find({"team_element_id" : x["team_element_id"]}).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]
					team_elements.append(existsing["_id"])

			written = []

			# TODO: Test
			for x in row["assignments"]:
				existsing = db.assignments.find({"title" : x["name"], "date" : x["date"], "team_elements" : { "$in" : team_elements}}).limit(1)

				data = {
					"title" : x["name"],
					"date" : x["date"]
				}

				if existsing.count() > 0:
					existsing = existsing[0]
					data["exercise_id"] = existsing["exercise_id"]

				written.append(data)

			created = row["created"]

			existsing = db.persons.find({"name" : str(created["teacher"]["name"]), "abbrevation" : str(created["teacher"]["abbrevation"]), "branch_id" : str(branch_id)})

			if existsing.count() > 0:
				existsing = existsing[0]

				created["teacher"]["_id"] = existsing["_id"]

			changed = row["changed"]

			existsing = db.persons.find({"name" : str(changed["teacher"]["name"]), "abbrevation" : str(changed["teacher"]["abbrevation"]), "branch_id" : str(branch_id)})

			if existsing.count() > 0:
				existsing = existsing[0]

				changed["teacher"]["_id"] = existsing["_id"]

			element = {
				"title" : row["title"],
				"phase_id" : str(phase_id),
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"note" : row["note"],
				"estimate" : row["estimate"],
				"changed" : changed,
				"teams" : row["teams"],
				"skills" : row["focus_points"],
				"work_methods" : row["methods"],
				"created" : created,
				"periods" : row["periods"],
				"activities" : activities,
				"written" : written
			}

			# Launch Activity Scraper

			status = sync.sync(db.phases, unique, element)

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