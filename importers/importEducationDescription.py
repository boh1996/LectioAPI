import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import description as descriptionApi

def importEducationDescription ( school_id, branch_id, team_element_id, session = False, username = False, password = False ):
	try:
		objectList = descriptionApi.description({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"team_element_id" : team_element_id,
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
			existsing = db.team_elements.find({"team_element_id" : str(team_element_id)}).limit(1)

			team_elements = []

			if existsing.count() > 0:
				existsing = existsing[0]

				if "team_id" in existsing:
					unique = {
						"team_id" : str(existsing["team_id"])
					}

					element = {
						"team_id" : str(existsing["team_id"]),
						"name" : objectList["information"]["team_name"],
						"terms" : objectList["information"]["terms"],
						"subject" : objectList["information"]["subject"],
						"school_id" : str(school_id),
						"branch_id" : str(branch_id),
					}

					existsing = db.subjects.find({"name" : objectList["information"]["subject"]["name"]}).limit(1)

					if existsing.count() > 0:
						existsing = existsing[0]
						element["subject"]["subject_id"] = existsing["subject_id"]

					status = sync.sync(db.teams, unique, element)

					existsing = db.teams.find(unique).limit(1)[0]
					if "team_elements" in existsing:
						team_elements = existsing["team_elements"]

			for row in objectList["phases"]:
				documents = []

				# TODO: Add link with document DB
				for x in row["documents"]:
					documents.append({
						"name" : x["name"]
					})

				written = []

				# TODO: Test
				for x in row["written"]:
					existsing = db.assignments.find({"title" : x["title"], "date" : x["date"], "team_elements" : { "$in" : team_elements}}).limit(1)

					data = {
						"title" : x["title"],
						"date" : x["date"]
					}

					if existsing.count() > 0:
						existsing = existsing[0]
						data["exercise_id"] = existsing["exercise_id"]

					written.append(data)

				unique = {
					"phase_id" : str(row["phase_id"])
				}

				element = {
					"school_id" : str(school_id),
					"branch_id" : str(branch_id),
					"phase_id" : str(row["phase_id"]),
					"reach" : row["reach"],
					"work_methods" : row["methods"],
					"skills" : row["focus_points"],
					"links" : row["links"],
					"name" : row["name"],
					"readings" : row["readings"],
					"description" : row["description"],
					"documents" : documents,
					"planned_written" : written,
					"title" : row["title"],
					"estimate" : row["estimate"]
				}

				status = sync.sync(db.phases, unique, element)

				# Launch Phase Importer

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