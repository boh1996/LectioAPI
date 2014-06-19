import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
from class_members import *

def importClassMembers ( school_id, branch_id, class_id, session = False, username = False, password = False ):
	try:
		objectList = class_members({
			"school_id" : school_id,
			"class_id" : class_id,
			"username" : username,
			"password" : password
		}, session)

		if objectList is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			members = []
			objects = objectList["students"] + objectList["teachers"]
			for row in objects:

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