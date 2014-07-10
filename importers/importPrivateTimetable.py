import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import timetable
from url_creator import *
import functions
import outgoing_censor
import exam_team
import activity_info
import private_activity
import authenticate

def importPrivateTimetable ( school_id, branch_id, student_id, username, password, number_of_weeks = 1 ):
	weeksInfo = functions.weeks(number_of_weeks)

	session = authenticate.authenticate({
		"school_id" : school_id,
		"branch_id" : branch_id,
		"username" : username,
		"password" : password
	})

	if session == False:
		error.log(__file__, False, "authenticate")
		return False

	url = timetable_url("student", school_id, branch_id, student_id)

	for week in weeksInfo["weeks"]:
		# If the year has to be incremented, increment it
		if week < weeksInfo["current_week"]:
			year = weeksInfo["start_year"]+1
		else:
			year = weeksInfo["start_year"]

		weekDateTime = datetime.strptime(str(year) + "-" + str(week) + "-" + "1", "%Y-%W-%w")

		data = None

		try:
			data =  timetable.timetable({
				"school_id" : school_id,
				"student_id" : student_id,
				"branch_id" : branch_id
			}, url, int(week), int(year), session)
		except Exception, e:
			error.log(__file__, False, str(e))

		if data is None:
			error.log(__file__, False, "Unknown Object")
			return

		if not "status" in data:
			error.log(__file__, False, "Unknown Object")
			return

		if data["status"] == "ok":
			unique = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id)
			}

			element = {
				"school_id" : str(school_id),
				"branch_id" : str(branch_id),
				"module_info" : data["module_info"]
			}

			status = sync.sync(db.schools, unique, element)

			for element in data["timetable"]:
				teachers = []
				teams = []

				if element["type"] == "school":
					for row in element["teachers"]:
						status = sync.sync(db.persons, {"teacher_id" : row["teacher_id"]}, {"teacher_id" : row["teacher_id"]})

						teachers.append(status["_id"])

					for row in element["teams"]:
						status = sync.sync(db.team_elements, {"team_element_id" : row["team_id"]}, {"team_element_id" : row["team_id"]})

						teams.append(status["_id"])

					unique = {
						"activity_id" : element["activity_id"],
						#"type" : "private"
					}

					element = {
						"teachers" : teachers,
						"activity_id" : str(element["activity_id"]),
						"school_id" : str(element["school_id"]),
						"branch_id" : str(branch_id),
						"text" : element["text"],
						"status" : element["status"],
						"start" : element["startTime"],
						"end" : element["endTime"],
						"event_type" : element["type"],
						"team_elements" : teams,
						"location_text" : element["location_text"],
						"room_text" : element["room_text"],
						#"type" : "private"
					}

					status = sync.sync(db.events, unique, element)

					# Launch Activity Info Scraper

					'''if sync.check_action_event(status) == True:
						# Launch Activity Info Sraper

						for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id, "activity_id" : element["activity_id"]}):
							sync.send_event(url, "event", element)

						# Teachers
						# Teams
						# Students'''
				elif element["type"] == "exam":
					# Launch Exam Scraper
					print "Exam"
				elif element["type"] == "outgoing_censor":
					# Launch Outgoing censor scraper
					print "outgoing_censor"
				elif element["type"] == "private":
					# Launch Private scraper
					print "private"

			# Infomation Elements
			for element in data["information"]:
				if "activity_id" in element:
					unique = {
						"date" : element["date"],
						"activity_id" : element["activity_id"],
						"school_id" : school_id,
						"branch_id" : branch_id,
						"week" : week,
						"term" : data["term"]["value"]
					}

					element = {
						"date" : element["date"],
						"message" : element["message"],
						"activity_id" : element["activity_id"],
						"status" : element["status"],
						"school_id" : school_id,
						"branch_id" : branch_id,
						"week" : week,
						"term" : data["term"]["value"]
					}
				else:
					unique = {
						"date" : element["date"],
						"message" : element["message"],
						"school_id" : school_id,
						"branch_id" : branch_id,
						"week" : week,
						"term" : data["term"]["value"]
					}

					element = {
						"date" : element["date"],
						"message" : element["message"],
						"school_id" : school_id,
						"branch_id" : branch_id,
						"week" : week,
						"term" : data["term"]["value"]
					}

				status = sync.sync(db.information, unique, element)

				if sync.check_action_event(status) == True:
					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "information", element)

			# Information Elements removed
			'''deleted = sync.find_deleted(db.information, {"school_id" : school_id, "branch_id" : branch_id, "term" : data["term"]["value"]}, ["message", "date", "week", "term", "school_id", "branch_id"], data["information"])

			for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
				sync.send_event(url, "information_deleted", element)'''
		else:
			if "error" in data:
				error.log(__file__, False, data["error"])
			else:
				error.log(__file__, False, "Unknown Error")

importPrivateTimetable(517, 4733693427, 4789793691, "boh1996", "jwn53yut", 1)