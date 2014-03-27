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
		if classObject["name"] == class_name:
			return classObject["class_id"]

def school ( school_id, branch_id ):
	try:
		classes = db.classes.find()
		studentsList = studentsApi.students({
			"school_id" : school_id,
			"branch_id" : branch_id
		})

		if studentsList is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in studentsList:
			error.log(__file__, False, "Unknown Object")
			return False

		if studentsList["status"] == "ok":
			for student in studentsList["students"]:
				uniqueStudent = {
					"student_id" : student["student_id"]
				}

				# Student element
				elementStudent = {
					"name" : student["name"],
					"student_id" : student["student_id"],
					"context_card_id" : student["context_card_id"],
					"status" : student["status"],
					"school_id" : student["school_id"],
					"branch_id" : student["branch_id"],
				}

				# Link student with a class
				uniqueClassStudent = {
					"class_id" : findClassId(student["class_name"], classes),
					"class_student_id" : student["class_student_id"],
					"student_id" : student["student_id"],
					"term" : studentsList["term"]["value"],
				}

				classStudentElement = {
					"class_id" : findClassId(student["class_name"], classes),
					"class_student_id" : student["class_student_id"],
					"student_id" : student["student_id"],
					"term" : studentsList["term"]["value"]
				}

				status = sync.sync(db.students, uniqueStudent, elementStudent)
				sync.sync(db.class_students, uniqueClassStudent, classStudentElement)

				if sync.check_action_event(status) == True:
					for url in sync.find_listeners('student', uniqueStudent):
						sync.send_event(url, status["action"], elementStudent)

					for url in sync.find_general_listeners('student_general'):
						sync.send_event(url, status["action"], elementStudent)

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