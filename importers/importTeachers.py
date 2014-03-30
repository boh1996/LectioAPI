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
					"teacher_id" : teacher["teacher_id"]
				}

				element = {
					"name" : teacher["name"],
					"initial" : teacher["initial"],
					"context_card_id" : teacher["context_card_id"],
					"teacher_id" : teacher["teacher_id"],
					"type" : teacher["type"],
					"school_id" : teacher["school_id"],
					"branch_id" : teacher["branch_id"]
				}

				status = sync.sync(db.teachers, unique, element)

				if sync.check_action_event(status) == True:
					for url in sync.find_listeners('teacher', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "teacher", element)

					for url in sync.find_general_listeners('teacher_general'):
						sync.send_event(url, status["action"], element)

			deleted = sync.find_deleted(db.rooms, {"school_id" : school_id, "branch_id" : branch_id}, ["teacher_id"], objectList["teachers"])

			for element in deleted:
				for url in sync.find_listeners('teacher', {"teacher_id" : element["teacher_id"]}):
					sync.send_event(url, 'deleted', element)

				for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
					sync.send_event(url, "teacher_deleted", element)


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