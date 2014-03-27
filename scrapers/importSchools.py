import schools as schoolsApi
from datetime import datetime
from pymongo import MongoClient
import database

try:
	schoolList = schoolsApi.schools()

	db = database.db

	if schoolList["status"] == "ok":
		for school in schoolList["schools"]:
			db.schools.update({
				"school_id" : school["school_id"],
				"branch_id" : school["branch_id"]
			},{
				"school_id" : school["school_id"],
				"branch_id" : school["branch_id"],
				"name" : school["name"]
			}, upsert=True)
	else:
		# Log Error
		pass
except Exception, e:
	print "Error: in api/school"
	print e
	# TODO: Log Error
	pass


