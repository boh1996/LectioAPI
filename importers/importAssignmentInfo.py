import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from pymongo import MongoClient
from database import *
import error
import sync
import assignment_info as assignmentInfoApi
import authenticate

def importAssignmentInfo ( school_id, branch_id, student_id, exercise_id, session = False, username = False, password = False ):
	try:
		objectList = assignmentInfoApi.assignment_info({
			"school_id" : school_id,
			"branch_id" : branch_id,
			"student_id" : student_id,
			"username" : username,
			"password" : password,
			"assignment_id" : str(exercise_id)
		}, session)

		if objectList is None:
				error.log(__file__, False, "Unknown Object")
				return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			row = objectList["information"]

			# Uploads
			comments = []

			for comment in row["comments"]:
				data = {
					"comment" : comment["comment"],
					"user" : {
						"context_card_id" : comment["uploader"]["context_card_id"]
					},
					"date" : comment["date"]
				}

				if len(comment["file"]["entry_id"]) > 1:
					unique = {
						"entry_id" : str(comment["file"]["entry_id"])
					}

					element = {
						"entry_id" : str(comment["file"]["entry_id"]),
						"type" : comment["file"]["type"],
						"school_id" : str(school_id),
						"branch_id" : str(branch_id),
						"date" : comment["date"],
						"name" : comment["file"]["name"],
						"user" : {
							"context_card_id" : comment["uploader"]["context_card_id"]
						}
					}

					status = sync.sync(db.documents, unique, element)

					# Launch Document Scraper

					data["document_id"] = status["_id"]

				comments.append(data)

			members = []

			for member in row["members"]:
				unique = {
					"student_id" : str(member["student_id"])
				}

				contextCards = []
				contextCards.append(member["context_card_id"])
				existsing = db.persons.find(unique).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]
					if "context_cards" in existsing:
						for card in existsing["context_cards"]:
							if not card in contextCards:
								contextCards.append(card)

				element = {
					"type" : "student",
					"student_id" : str(member["student_id"]),
					"name" : unicode(str(member["name"]).decode("utf8")),
					"class_student_id" : unicode(str(member["student_class_code"]).decode("utf8")),
					"context_cards" : contextCards,
					"school_id" : str(school_id),
					"branch_id" : str(branch_id)
				}

				status = sync.sync(db.persons, unique, element)

				members.append(status["_id"])

			documents = []

			for document in row["documents"]:
				unique = {
					"exercise_file_id" : str(document["exercise_file_id"])
				}

				element = {
					"school_id" : str(school_id),
					"branch_id" : str(branch_id),
					"exercise_file_id" : str(document["exercise_file_id"]),
					"type" : document["type"],
					"name" : document["name"],
					"uploaded_date_string" : document["uploaded_date_string"]
				}

				status = sync.sync(db.documents, unique, element)

				# Launch Document Scraper

				documents.append(status["_id"])

			availableStudents = []

			for student in row["group"]["available_students"]:
				unique = {
					"student_id" : str(student["student_id"])
				}

				contextCards = []
				contextCards.append("S" + student["student_id"])
				existsing = db.persons.find(unique).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]
					if "context_cards" in existsing:
						for card in existsing["context_cards"]:
							if not card in contextCards:
								contextCards.append(card)

				element = {
					"type" : "student",
					"student_id" : str(student["student_id"]),
					"name" : unicode(str(student["name"]).decode("utf8")),
					"class_student_id" : unicode(str(student["student_class_code"]).decode("utf8")),
					"context_cards" : contextCards,
					"school_id" : str(school_id),
					"branch_id" : str(branch_id)
				}

				status = sync.sync(db.persons, unique, element)

				availableStudents.append(status["_id"])

			teachers = []

			for teacher in row["teachers"]:
				unique = {
					"teacher_id" : str(teacher["teacher_id"])
				}

				contextCards = []
				contextCards.append(teacher["context_card_id"])
				existsing = db.persons.find(unique).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]
					if "context_cards" in existsing:
						for card in existsing["context_cards"]:
							if not card in contextCards:
								contextCards.append(card)

				element = {
					"type" : "teacher",
					"teacher_id" : str(teacher["teacher_id"]),
					"name" : unicode(str(teacher["name"]).decode("utf8")),
					"context_cards" : contextCards,
					"abbrevation" : teacher["abbrevation"],
					"school_id" : str(school_id),
					"branch_id" : str(branch_id)
				}

				status = sync.sync(db.persons, unique, element)

				teachers.append(status["_id"])

			team_elements = []

			for team_element in row["team"]:
				unique = {
					"team_element_id" : team_element["team_element_id"]
				}

				contextCards = []
				contextCards.append(team_element["context_card_id"])
				existsing = db.persons.find(unique).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]
					if "context_cards" in existsing:
						for card in existsing["context_cards"]:
							if not card in contextCards:
								contextCards.append(card)

				element = {
					"team_element_id" : team_element["team_element_id"],
					"name" : team_element["team_element_name"],
					"context_cards" : contextCards
				}

				status = sync.sync(db.team_elements, unique, element)

				team_elements.append(status["_id"])

			unique = {
				"exercise_id" : str(exercise_id),
				"student_id" : str(student_id)
			}

			element = {
				"exercise_id" : str(exercise_id),
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"student_id" : str(student_id),
				"team_elements" : team_elements,
				"student_note" : row["student"]["student_note"],
				"grade_note" : row["student"]["grade_note"],
				"status" : row["student"]["status"],
				"grade" : row["student"]["grade"],
				"leave" : row["student"]["leave"],
				"finished" : row["student"]["finished"],
				"waiting_for" : row["student"]["waiting_for"],
				"comments" : comments,
				"members" : members,
				"documents" : documents,
				"group" : {
					"available_students" : availableStudents
				},
				"title" : row["title"],
				"date" : row["date"],
				"hours" : row["student_time"],
				"grading_scale" : row["grading_scale"],
				"note" : row["note"],
				"in_instruction_detail" : str(row["in_instruction_detail"]),
				"teachers" : teachers,
				"group_assignment" : str(row["group_assignment"])
			}

			status = sync.sync(db.assignments, unique, element)

			return True
		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
				return False
			else:
				error.log(__file__, False, "Unknown error")

	except Exception, e:
		error.log(__file__, False, str(e))
		return False