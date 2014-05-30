#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import time
from time import mktime
import functions

def exam_team ( config ):
	url = "https://www.lectio.dk/lectio/%s/proevehold.aspx?type=proevehold&ProeveholdId=%s" % ( str(config["school_id"]), str(config["test_team_id"]) )

	cookies = {}

	# Insert User-agent headers and the cookie information
	headers = {
		"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
		"Content-Type" : "application/x-www-form-urlencoded",
		"Host" : "www.lectio.dk",
		"Origin" : "https://www.lectio.dk",
		"Cookie" : functions.implode(cookies, "{{index}}={{value}}", "; ")
	}

	response = proxy.session.get(url, headers=headers)

	html = response.text

	soup = Soup(html)

	if soup.find("div", attrs={"id" : "m_Content_LectioDetailIslandProevehold_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	tables = soup.find("div", attrs={"id" : "m_Content_LectioDetailIslandProevehold_pa"}).findAll("table")
	oneDayProg = re.compile(r"(?P<day>.*)\/(?P<month>.*)-(?P<year>.*)")
	dateTimeProg = re.compile(r"(?P<day>.*)\/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*)")
	dayTimeProg = re.compile(r"(?P<day>.*)\/(?P<month>.*) (?P<hour>.*):(?P<minute>.*)")
	multiDayProg = re.compile(r"(?P<start_day>.*)\/(?P<start_month>.*)-(?P<start_year>.*) - (?P<end_day>.*)\/(?P<end_month>.*)-(?P<end_year>.*)")

	informationElements = tables[0].findAll("td")

	teamNameProg = re.compile(r"(?P<team_full_name>.*) \((?P<team_class>.*) (?P<subject_abbrevation>.*)\)")
	teamNameGroups = teamNameProg.match(informationElements[5].text)
	teamNameAlternativeProg = re.compile(r"(?P<team_full_name>.*) \((?P<class_number>) (?P<team_class>.*) (?P<team_name>.*)\)")
	teamNameAlternativeGroups = teamNameAlternativeProg.match(informationElements[5].text)

	xprsProg = re.compile(r"(?P<code>.*) (?P<type>.*) (?P<subject_name>.*)")
	xprsGroups = xprsProg.match(unicode(informationElements[7].text))
	xprs_type = xprsGroups.group("type") if not xprsGroups is None else ""

	test_type = informationElements[11].text

	rooms = []
	roomNameProg = re.compile(r"(?P<room_number>.*) ?(?P<other_name>.*)? - (?P<room_name>.*) \((?P<exam_room_type>.*)\)")

	for room in informationElements[13].text.split(", "):
		roomNameGroups = roomNameProg.match(room)
		room_type = roomNameGroups.group("exam_room_type") if not roomNameGroups is None else ""
		room_number = roomNameGroups.group("room_number") if not roomNameGroups is None else ""
		room_other_name_extension = room_number.split(" ")[1] if len(room_number.split(" ")) > 1 else ""
		rooms.append({
			"room_number" : room_number.split(" ")[0],
			"room_name" : unicode(roomNameGroups.group("room_name")) if not roomNameGroups is None else "",
			"other_name" : unicode(room_other_name_extension + roomNameGroups.group("other_name")) if not roomNameGroups is None and "other_name" in roomNameGroups.groupdict() else unicode(room_other_name_extension),
			"exam_room_type" : "preparation" if room_type == "Forberedelse" else "examination"
		})

	students = []
	studentRows = tables[1].findAll("tr")
	headers = studentRows[0].findAll("td")
	studentRows.pop(0)

	examStart = None
	examEnd = None
	preperationStart = None
	preperationEnd = None
	eventStart = None
	eventEnd = None

	longPreperationTime = False
	preperation = False
	inGroups = False

	if headers[len(headers)-1].text == "Gruppe slut":
		inGroups = True

	studentClassIdProg = re.compile(r"(?P<class_name>.*) (?P<student_class_id>.*)")

	for student in studentRows:
		groupStart = None
		groupEnd = None
		studentPreperationStart = None
		studentPreperationEnd = None
		group_number = None

		elements = student.findAll("td")

		studentClassIdGrups = studentClassIdProg.match(elements[0].text)
		studentClassIdFull = elements[0].text
		name = unicode(elements[1].text)
		class_code = elements[2].text

		if inGroups is True:
			startDayGroups = oneDayProg.match(elements[3].text)
			endDayGroups = oneDayProg.match(elements[3].text)
			studentStartTime = elements[4].text
			studentEndTime = elements[5].text
			group_number = elements[6].text

			groupStart = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(startDayGroups.group("day")), functions.zeroPadding(startDayGroups.group("month")), "20" + startDayGroups.group("year"), elements[7].text), "%d/%m-%Y %H:%M")
			groupEnd = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(startDayGroups.group("day")), functions.zeroPadding(startDayGroups.group("month")), "20" + startDayGroups.group("year"), elements[8].text), "%d/%m-%Y %H:%M")
		elif headers[3].text == "Lang forb. start":
			longPreperationTime = True

			startDayGroups = oneDayProg.match(elements[4].text)
			endDayGroups = oneDayProg.match(elements[4].text)
			studentStartTime = elements[5].text
			studentEndTime = elements[6].text

			longPreperationGroups = dayTimeProg.match(elements[3].text)

			studentPreperationStartTime =  longPreperationGroups.group("hour") + ":" + longPreperationGroups.group("minute")

			studentPreperationStart = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(longPreperationGroups.group("day")), functions.zeroPadding(longPreperationGroups.group("month")), "20" + startDayGroups.group("year"), studentPreperationStartTime), "%d/%m-%Y %H:%M")
			studentPreperationEnd = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(startDayGroups.group("day")), functions.zeroPadding(startDayGroups.group("month")), "20" + startDayGroups.group("year"), studentStartTime), "%d/%m-%Y %H:%M")
		elif headers[4].text == "Forb.":
			preperation = True

			startDayGroups = oneDayProg.match(elements[3].text)
			endDayGroups = oneDayProg.match(elements[3].text)
			studentStartTime = elements[5].text
			studentEndTime = elements[6].text

			studentPreperationStartTime =  elements[4].text

			studentPreperationStart = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(startDayGroups.group("day")), functions.zeroPadding(startDayGroups.group("month")), "20" + startDayGroups.group("year"), studentPreperationStartTime), "%d/%m-%Y %H:%M")
			studentPreperationEnd = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(startDayGroups.group("day")), functions.zeroPadding(startDayGroups.group("month")), "20" + startDayGroups.group("year"), studentStartTime), "%d/%m-%Y %H:%M")
		else:
			startDayGroups = oneDayProg.match(elements[3].text)
			endDayGroups = startDayGroups
			studentStartTime = elements[4].text
			studentEndTime = elements[5].text

		studentStart = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(startDayGroups.group("day")), functions.zeroPadding(startDayGroups.group("month")), "20" + startDayGroups.group("year"), studentStartTime), "%d/%m-%Y %H:%M")
		studentEnd = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(endDayGroups.group("day")), functions.zeroPadding(endDayGroups.group("month")), "20" + endDayGroups.group("year"),studentEndTime), "%d/%m-%Y %H:%M")

		if preperationStart is None:
			preperationStart = studentPreperationStart
		elif studentPreperationStart < preperationStart:
			preperationStart = studentPreperationStart

		if preperationEnd is None:
			preperationEnd = studentPreperationEnd
		elif studentPreperationEnd < preperationEnd:
			preperationEnd = studentPreperationEnd

		if examStart is None:
			examStart = studentStart
		elif studentStart < examStart:
			examStart = studentStart

		if examEnd is None:
			examEnd = studentEnd
		elif studentEnd > examEnd:
			examEnd = studentEnd

		if preperationStart is None:
			eventStart = examStart
		else:
			eventStart = preperationStart

		eventEnd = examEnd

		students.append({
			"student_class_id_full" : studentClassIdFull,
			"student_class_id" : studentClassIdGrups.group("student_class_id") if not studentClassIdGrups is None else "",
			"class_name" : studentClassIdGrups.group("class_name") if not studentClassIdGrups is None else "",
			"class_code" : class_code,
			"name" : name,
			"is_group" : inGroups,
			"group_number" : group_number,
			"group_time" : {
				"start" : groupStart,
				"end" : groupEnd
			},
			"examination" : {
				"start" : studentStart,
				"end" : studentEnd
			},
			"preperation_type" : "long" if longPreperationTime is True else "normal" if preperation is True else "none",
			"preperation" : {
				"start" : studentPreperationStart,
				"end" : studentPreperationEnd
			}
		})

	teachers = []
	teacherProg = re.compile(r"(?P<abbrevation>.*) - (?P<name>.*)")
	for teacher in informationElements[3].contents:
		if len(teacher) > 1 and not unicode(teacher) == u"<br/>":
			teacherGroups = teacherProg.match(unicode(teacher))
			teachers.append({
				"name" : unicode(teacherGroups.group("name")) if not teacherGroups is None else "",
				"abbrevation" : unicode(teacherGroups.group("abbrevation")) if not teacherGroups is None else ""
			})

	censors = []
	censorProg = re.compile(r"(?P<censor_id>.*) - (?P<censor_name>.*)")
	for censor in informationElements[9].contents:
		if censor and not str(censor) == str("<br/>"):
			censorGroups = censorProg.match(str(censor))
			censors.append({
				"censor_id" : unicode(censorGroups.group("censor_id")) if not censorGroups is None else "",
				"name" : unicode(censorGroups.group("censor_name")) if not censorGroups is None else ""
			})

	if not teamNameGroups is None:
		team = {
			"full_name" : unicode(teamNameGroups.group("team_full_name")) if not teamNameGroups is None else "",
			"team_class" : unicode(teamNameGroups.group("team_class")) if not teamNameGroups is None else "",
			"subject_abbrevation" : unicode(teamNameGroups.group("subject_abbrevation")) if not teamNameGroups is None else "",
		}
	elif not teamNameAlternativeGroups is None:
		team = {
			"full_name" : unicode(teamNameAlternativeGroups.group("team_full_name")) if not teamNameAlternativeGroups is None else "",
			"team_class" : unicode(teamNameAlternativeGroups.group("team_class")) if not teamNameAlternativeGroups is None else "",
			"class_number" : unicode(teamNameAlternativeGroups.group("class_number")) if not teamNameAlternativeGroups is None else "",
			"team_name" : unicode(teamNameAlternativeGroups.group("team_name")) if not teamNameAlternativeGroups is None else "",
		}
	else:
		team = {
			"full_name" : unicode(informationElements[5].text)
		}

	information = {
		"test_team_name" : unicode(informationElements[1].text),
		"teachers" : teachers,
		"students" : students,
		"censors" : censors,
		"team" : team,
		"xprs_test" : True if not informationElements[7].text == "(ikke XPRS eksamen)" else False,
		"xprs" : {
			"full_name" : unicode(informationElements[7].text),
			"code" : xprsGroups.group("code") if not xprsGroups is None else "",
			"type" : "written" if xprs_type == "SKR" else "combined" if xprs_type == "SAM" else "oral" if xprs_type == "MDT" else "other",
			"subject" : xprsGroups.group("subject_name") if not xprsGroups is None else ""
		},
		"test_type" : "written" if test_type == "Skriftlig eksamen" else "oral" if test_type == "Mundtlig eksamen" else "combined" if test_type == "Samlet vurdering" else "other",
		"number_of_students" : informationElements[19].text,
		"note" : unicode(informationElements[17].text) if len(unicode(informationElements[17].text)) > 1 else "",
		"rooms" : rooms,
		"time" : {
			"start" : examStart,
			"end" : examEnd
		},
		"preperation" : {
			"start" : preperationStart,
			"end" : preperationEnd
		},
		"group_examination" : inGroups,
		"preperation_type" : "long" if longPreperationTime is True else "normal" if preperation is True else "none",
		"event" : {
			"start" : eventStart,
			"end" : eventEnd
		}
	}

	return {
		"status" : "ok",
		"information" : information
	}