import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import materials as materialsApi

def importMaterials ( school_id, branch_id, team_element_id ):
	try:
		objectList = materialsApi.materials({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"team_element_id" : team_element_id
		})

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			unique = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_element_id" : str(team_element_id)
			}

			element = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"team_element_id" : str(team_element_id),
				"materials" : objectList["materials"]
			}

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
importMaterials(517, 4733693427, 5936142236)