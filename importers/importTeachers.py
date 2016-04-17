import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import teachers as teachersApi

def importTeachers ( school_id, branch_id ):
	try:
		teachersList = teachersApi.teachers({
			"school_id" : school_id,
			"branch_id" : branch_id
		})

		if teachersList is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in teachersList:
			error.log(__file__, False, "Unknown Object")
			return False

		if teachersList["status"] == "ok":
			for teacher in teachersList["teachers"]:
				unique = {
					"teacher_id" : str(teacher["teacher_id"])
				}

				contextCards = []
				contextCards.append(teacher["context_card_id"])
				existsing = db.persons.find(unique).limit(1)

				terms = []

				if existsing.count() > 0:
					existsing = existsing[0]
					if "context_cards" in existsing:
						for row in existsing["context_cards"]:
							if not row in contextCards:
								contextCards.append(row)

					if "terms" in existsing:
						terms = existsing["terms"]

				if not teachersList["term"]["value"] in terms:
					terms.append(teachersList["term"]["value"])

				element = {
					"name" : unicode(str(teacher["name"]).decode("utf8")),
					"abbrevation" : unicode(teacher["initial"].decode("utf8")),
					"context_cards" : contextCards,
					"teacher_id" : str(teacher["teacher_id"]),
					"school_id" : str(teacher["school_id"]),
					"branch_id" : str(teacher["branch_id"]).replace("L", ""),
					"type" : "teacher",
					"terms" : terms
				}

				status = sync.sync(db.persons, unique, element)

				'''if sync.check_action_event(status) == True:
					# Launch Context Card Teacher Scraper, Optional

					for url in sync.find_listeners('teacher', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "teacher", element)

					for url in sync.find_general_listeners('teacher_general'):
						sync.send_event(url, status["action"], element)'''

			'''deleted = sync.find_deleted(db.persons, {"school_id" : school_id, "branch_id" : branch_id, "type" : "teacher"}, ["teacher_id"], teachersList["teachers"])

			for element in deleted:
				for url in sync.find_listeners('teacher', {"teacher_id" : element["teacher_id"]}):
					sync.send_event(url, 'deleted', element)

				for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
					sync.send_event(url, "teacher_deleted", element)'''


			return True
		else:
			if "error" in teachersList:
				error.log(__file__, False, teachersList["error"])
				return False
			else:
				error.log(__file__, False, "Unknown Error")
				return False
	except Exception, e:
		error.log(__file__, False, str(e))
		return False