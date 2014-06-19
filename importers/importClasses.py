import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
import database
import error
import sync
import classes as classesApi

def importClasses ( school_id, branch_id, term = False ):
	try:
		classList = classesApi.classes({
			"school_id" : school_id,
			"branch_id" : branch_id
		}, term)

		db = database.db

		if classList is None:
			error.log(__file__, False, "Unknown Object")
			return

		if not "status" in classList:
			error.log(__file__, False, "Unknown Object")
			return

		if classList["status"] == "ok":
			for classObject in classList["classes"]:
				unique = {
					"school_id" : classObject["school_id"],
					"branch_id" : classObject["branch_id"],
					"class_id" : classObject["class_id"]
				}

				names = []
				names.append({
					"term" : str(classList["term"]["value"]),
					"name" : unicode(str(classObject["name"]).decode("utf8"))
				})

				existsing = db.classes.find(unique).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]

					if "names" in existsing:
						if "names" in existsing:
							for row in existsing["names"]:
								if not row["term"] == classList["term"]["value"]:
									names.append(row)
				element = {
					"names" : names,
					"school_id" : classObject["school_id"],
					"branch_id" : classObject["branch_id"],
					"class_id" : classObject["class_id"],
					"type" : classObject["type"]
				}

				status = sync.sync(db.classes, unique, element)

				if sync.check_action_event(status) == True:
					for url in sync.find_listeners('class', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "class", element)

					for url in sync.find_general_listeners('class_general'):
						sync.send_event(url, status["action"], element)

					# Launch class_members scraper
					# Launch class teams

		else:
			if "error" in classList:
				error.log(__file__, False, classList["error"])
			else:
				error.log(__file__, False, "Unknown Error")
	except Exception, e:
		print str(e)
		error.log(__file__, False, str(e))

importClasses(517, 4733693427)