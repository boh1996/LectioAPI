import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
import database
import error
import sync
from school_info import *

db = database.db

# Retrieves the schools from Lecito, syncs with DB and sends out events
def importSchoolInfo ( school_id ):
	try:
		info = school_info({
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
				"school_id" : str(school_id),
				"branch_id" : info["information"]["branch_id"]
			}

			element = {
				"school_id" : str(school_id),
				"branch_id" : info["information"]["branch_id"],
				"terms" : info["information"]["terms"],
				"name" : info["information"]["name"]
			}

			status = sync.sync(db.schools, unique, element)

		else:
			if "error" in info:
				error.log(__file__, False, info["error"])
			else:
				error.log(__file__, False, "Unknown Error")
	except Exception, e:
		error.log(__file__, False, str(e))