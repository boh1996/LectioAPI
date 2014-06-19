import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
import schools as schoolsApi
from datetime import datetime
from pymongo import MongoClient
import database
import error
import sync

# Retrieves the schools from Lecito, syncs with DB and sends out events
def importSchools ():
	try:
		schoolList = schoolsApi.schools()

		db = database.db

		if schoolList["status"] == "ok":
			for school in schoolList["schools"]:
				status = sync.sync(db.schools, {
					"school_id" : school["school_id"],
					"branch_id" : school["branch_id"]
				},{
					"school_id" : school["school_id"],
					"branch_id" : school["branch_id"],
					"name" : school["name"]
				})

				if sync.check_action_event(status) == True:
					# Launch School_info Scraper
					# Launch Addres scraper

					for url in sync.find_listeners('school', {
						"school_id" : school["school_id"],
						"branch_id" : school["branch_id"]
					}):
						sync.send_event(url, status["action"], {
							"school_id" : school["school_id"],
							"branch_id" : school["branch_id"],
							"name" : school["name"]
						})

					for url in sync.find_general_listeners('school_general'):
						sync.send_event(url, status["action"], {
							"school_id" : school["school_id"],
							"branch_id" : school["branch_id"],
							"name" : school["name"]
						})

		else:
			if "error" in schoolList:
				error.log(__file__, False, schoolList["error"])
			else:
				error.log(__file__, False, "Unknown Error")
	except Exception, e:
		error.log(__file__, False, str(e))


