#!/usr/bin/python
# -*- coding: utf8 -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import students as studentsApi

def findClassId( class_name, classes ):
	for classObject in classes:
		if unicode(classObject["name"]) == unicode(class_name):
			return classObject["class_id"]

	return ""
def importStudents ( school_id, branch_id ):
	try:
		studentsList = studentsApi.students({
			"school_id" : school_id,
			"branch_id" : branch_id
		})

		'''classes = db.classes.find({"term" : studentsList["term"]["value"]})

		classList = []

		for classObject in classes:
			classList.append({
				"name" : classObject["name"],
				"class_id" : classObject["class_id"]
			})'''

		if studentsList is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in studentsList:
			error.log(__file__, False, "Unknown Object")
			return False

		if studentsList["status"] == "ok":
			for student in studentsList["students"]:
				#class_id = findClassId(student["class_name"], classList)

				unique = {
					"student_id" : str(student["student_id"])
				}

				contextCards = []
				contextCards.append(student["context_card_id"])
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

				if not studentsList["term"]["value"] in terms:
					terms.append(studentsList["term"]["value"])

				# Student element
				element = {
					"name" : unicode(str(student["name"]).decode("utf8")),
					"student_id" : str(student["student_id"]),
					"context_cards" : contextCards,
					"status" : unicode(str(student["status"]).decode("utf8")),
					"school_id" : str(student["school_id"]),
					"branch_id" : str(student["branch_id"]),
					"type" : "student",
					"terms" : terms
				}

				'''# Link student with a class
				uniqueClassStudent = {
					"class_id" : class_id,
					"class_student_id" : student["class_student_id"],
					"student_id" : student["student_id"],
					"term" : studentsList["term"]["value"],
				}

				classStudentElement = {
					"class_id" : class_id,
					"class_student_id" : student["class_student_id"],
					"student_id" : student["student_id"],
					"term" : studentsList["term"]["value"],
					"class_name" : student["class_name"]
				}'''

				status = sync.sync(db.persons, unique, element)
				#sync.sync(db.class_students, uniqueClassStudent, classStudentElement)

				'''if sync.check_action_event(status) == True:
					for url in sync.find_listeners('student', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "student", element)

					for url in sync.find_general_listeners('student_general'):
						sync.send_event(url, status["action"], element)'''

			'''deleted = sync.find_deleted(db.persons, {"school_id" : school_id, "branch_id" : branch_id, "type" : "student"}, ["student_id"], studentsList["students"])

			for element in deleted:
				for url in sync.find_listeners('student', {"student_id" : element["student_id"]}):
					sync.send_event(url, 'deleted', element)

				for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
					sync.send_event(url, "student_deleted", element)'''

			return True
		else:
			if "error" in studentsList:
				error.log(__file__, False, studentsList["error"])
				return False
			else:
				error.log(__file__, False, "Unknown Error")
				return False
	except Exception, e:
		error.log(__file__, False, str(e))
		return False