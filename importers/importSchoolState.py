import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
import database
import error
import sync
import school_state as schoolStateApi

db = database.db

# Retrieves the schools from Lecito, syncs with DB and sends out events
def importSchoolState ( school_id ):
	try:
		info = schoolStateApi.school_state({
			"school_id" : str(school_id)
		})

		if info is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in info:
			error.log(__file__, False, "Unknown Object")
			return False

		if info["status"] == "ok":
			unique = {
				"school_id" : str(school_id)
			}

			element = {
				"school_id" : str(school_id),
				"state" : info["state"],
				"active" : "True" if info["state"] == "ok" else "False"
			}

			status = sync.sync(db.schools, unique, element)

		else:
			if "error" in info:
				error.log(__file__, False, info["error"])
			else:
				error.log(__file__, False, "Unknown Error")
	except Exception, e:
		error.log(__file__, False, str(e))