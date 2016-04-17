import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import books as booksApi

def importBooks ( school_id, branch_id, student_id, session = False, username = False, password = False ):
	try:
		objectList = booksApi.books({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"student_id" : student_id,
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
			books = []

			for row in objectList["loans"]:
				unique = {
					"title" : row["title"]
				}

				element = {
					"title" : row["title"],
					"price" : row["price"]
				}

				status = sync.sync(db.books, unique, element)

				row["_id"] = status["_id"]

				existing = db.team_elements.find({"name" : row["team_name"], "school_id" : str(school_id), "branch_id" : str(branch_id)})

				if existing.count() > 0:
					if "team_id" in existing[0]:
						row["team_id"] = existing[0]["team_id"]

					row["team_element_id"] = existing[0]["team_element_id"]
				else:
					existing = db.teams.find({"name" : row["team_name"], "school_id" : str(school_id), "branch_id" : str(branch_id)})

					if existing.count() > 0:
						row["team_id"] = existing[0]["team_id"]

				books.append(row)

			unique = {
				"student_id" : str(student_id)
			}

			element = {
				"student_id" : str(student_id),
				"books" : books
			}

			status = sync.sync(db.persons, unique, element)

		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
				return False
			else:
				error.log(__file__, False, "Unknown error")

	except Exception, e:
		error.log(__file__, False, str(e))
		return False