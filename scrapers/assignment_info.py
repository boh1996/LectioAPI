#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import time
from time import mktime
import values
import codecs
import functions
import authenticate

def assignment_info ( config, session = False ):
	url = urls.assignment_info.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{ASSIGNMENT_ID}}", str(config["assignment_id"])).replace("{{STUDENT_ID}}",str(config["student_id"]))

	if session is False:
		session = authenticate.authenticate(config)

	if session == False:
		return {"status" : "error", "type" : "authenticate"}

	# Insert the session information from the auth function
	cookies = {
		"lecmobile" : "0",
		"ASP.NET_SessionId" : session["ASP.NET_SessionId"],
		"LastLoginUserName" : session["LastLoginUserName"],
		"lectiogsc" : session["lectiogsc"],
		"LectioTicket" : session["LectioTicket"]
	}

	settings = {}

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

	dateTime = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*)")

	if soup.find("div", attrs={"id" : "m_Content_registerAfl_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	teacherProg = re.compile(r"(?P<name>.*) \((?P<abbrevation>.*)\)")
	documentProg = re.compile(r"(?P<name>.*) \((?P<upload_date>.*)\)")
	teamProg = re.compile(r"(?P<class_name>.*) (?P<subject_name>.*)")

	rows = soup.find("div", attrs={"id" : "m_Content_registerAfl_pa"}).find("table").findAll("td")
	headers = soup.find("div", attrs={"id" : "m_Content_registerAfl_pa"}).find("table").findAll("th")
	rowMap = functions.mapRows(headers, rows)

	dateTimeGroups = dateTime.match(rowMap["Afleveringsfrist"].text)

	date = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateTimeGroups.group("day")), functions.zeroPadding(dateTimeGroups.group("month")), dateTimeGroups.group("year"), dateTimeGroups.group("hour"), dateTimeGroups.group("minute")), "%d/%m-%Y %H:%M")

	group_assignment = False
	members = []
	teachers = []
	teams = []
	documents = []
	uploads = []

	uploadRows = soup.find("table", attrs={"id" : "m_Content_RecipientGV"}).findAll("tr")
	uploadRows.pop(0)
	uploadProg = re.compile(r"\/lectio/(?P<school_id>.*)\/ExerciseFileGet.aspx\?type=(?P<type>.*)&entryid=(?P<entry_id>.*)")

	for row in uploadRows:
		elements = row.findAll("td")
		context_card_id = elements[1].find("span")["lectiocontextcard"]
		dateTimeGroups = dateTime.match(elements[0].find("span").text)
		upload_type = ""
		entry_id = ""
		if not elements[3].find("a") is None:
			uploadGroups = uploadProg.match(elements[3].find("a")["href"])
			entry_id = uploadGroups.group("entry_id")
			upload_type = uploadGroups.group("type")


		uploadDate = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateTimeGroups.group("day")), functions.zeroPadding(dateTimeGroups.group("month")), dateTimeGroups.group("year"), dateTimeGroups.group("hour"), dateTimeGroups.group("minute")), "%d/%m-%Y %H:%M")

		uploads.append({
			"file" : {
				"name" : unicode(elements[3].find("a").text) if not elements[3].find("a") is None else "",
				"entry_id" : entry_id,
				"type" : upload_type
			},
			"comment" : unicode(functions.cleanText(elements[2].text)),
			"uploader" : {
				"name" : unicode(elements[1].find("span")["title"]) if context_card_id[0] == "T" else unicode(elements[1].find("span").text),
				"type" : "teacher" if context_card_id[0] == "T" else "student",
				"person_id" : context_card_id.replace("T", "") if context_card_id[0] == "T" else context_card_id.replace("S", ""),
				"context_card_id" : context_card_id,
				"abbrevation" : unicode(elements[1].find("span").text) if context_card_id[0] == "T" else ""
			},
			"date" : uploadDate
		})

	documentIdProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/ExerciseFileGet.aspx\?type=(?P<type>.*)&exercisefileid=(?P<exercise_file_id>.*)")

	statusProg = re.compile(r"(?P<status>.*)\/ (.*): (?P<leave>.*)%")
	studentDataElements = soup.find("table", attrs={"id" : "m_Content_StudentGV"}).findAll("tr")[1].findAll("td")
	statusGroups = statusProg.match(unicode(functions.cleanText(studentDataElements[3].text)))
	status = functions.cleanText(statusGroups.group("status")) if not statusGroups is None else ""
	studentData = {
		"student" : {
			"context_card_id" : studentDataElements[0].find("img")["lectiocontextcard"],
			"student_id" : studentDataElements[0].find("img")["lectiocontextcard"].replace("S", ""),
		},
		"status" : "delivered" if status.strip() == "Afleveret" else "missing",
		"waiting_for" : "student" if functions.cleanText(studentDataElements[2].text) == "Elev" else "teacher" if unicode(functions.cleanText(studentDataElements[2].text)) == u"Lærer" else "none",
		"leave" : functions.cleanText(statusGroups.group("leave")) if not statusGroups is None else 0,
		"finished" : True if soup.find("input", attrs={"id" : "m_Content_StudentGV_ctl02_CompletedCB"}).has_attr("checked") and soup.find("input", attrs={"id" : "m_Content_StudentGV_ctl02_CompletedCB"})["checked"] == "checked" else False,
		"grade" : unicode(functions.cleanText(studentDataElements[5].text)),
		"grade_note" : unicode(functions.cleanText(studentDataElements[6].text)),
		"student_note" : unicode(functions.cleanText(studentDataElements[7].text))
	}

	if u"Opgavebeskrivelse" in rowMap:
		for row in rowMap[u"Opgavebeskrivelse"].findAll("a"):
			fileNameGroups = documentProg.match(functions.cleanText(row.text.strip()))
			fileIdGroups = documentIdProg.match(row["href"])
			documents.append({
				"name" : fileNameGroups.group("name") if not fileNameGroups is None else "",
				"exercise_file_id" : fileIdGroups.group("exercise_file_id") if not fileIdGroups is None else "",
				"uploaded_date_string" : fileNameGroups.group("upload_date") if not fileNameGroups is None else "",
				"type" : fileIdGroups.group("type") if not fileIdGroups is None else "",
				"school_id" : fileIdGroups.group("school_id") if not fileIdGroups is None else ""
			})

	for row in rowMap["Hold"].findAll("span"):
		teamGroups = teamProg.match(row.text)
		teams.append({
			"class_name" : unicode(teamGroups.group("class_name")) if not teamGroups is None else "",
			"subject_name" : unicode(teamGroups.group("subject_name")) if not teamGroups is None else "",
			"team_element_id" : rowMap["Hold"].find("span")["lectiocontextcard"].replace("HE", ""),
			"context_card_id" : rowMap["Hold"].find("span")["lectiocontextcard"]
		})

	for row in rowMap["Ansvarlig"].findAll("span"):
		teacherGroups = teacherProg.match(row.text)
		teachers.append({
			"teacher_id" : row["lectiocontextcard"].replace("T", ""),
			"name" : unicode(teacherGroups.group("name")) if not teacherGroups is None else "",
			"context_card_id" : row["lectiocontextcard"],
			"abbrevation" : unicode(teacherGroups.group("abbrevation")) if not teacherGroups is None else ""
		})

	if soup.find("div", attrs={"id" : "m_Content_groupIsland_pa"}):
		group_assignment = True
		memberRows = soup.find("table", attrs={"id" : "m_Content_groupMembersGV"}).findAll("tr")
		memberRows.pop(0)
		memberProg = re.compile(r"(?P<name>.*), (?P<code>.*)")

		for row in memberRows:
			elements = row.findAll("td")
			memberGroups = memberProg.match(elements[0].find("span").text)
			members.append({
				"name" : memberGroups.group("name") if not memberGroups is None else "",
				"student_id" : elements[0].find("span")["lectiocontextcard"].replace("S", ""),
				"context_card_id" : elements[0].find("span")["lectiocontextcard"],
				"student_class_code" : memberGroups.group("code") if not memberGroups is None else ""
			})
	else:
		members.append({
			"student_id" : config["student_id"]
		})

	availableStudents = []
	availableStudentProg = re.compile(r"(?P<name>.*) \((?P<code>.*)\)")

	if not soup.find("select", attrs={"id" : "m_Content_groupStudentAddDD"}) is None:

		for row in soup.find("select", attrs={"id" : "m_Content_groupStudentAddDD"}).findAll("option"):
			progGroups = availableStudentProg.match(row.text)
			availableStudents.append({
				"name" : unicode(progGroups.group("name")),
				"student_id" : row["value"],
				"student_class_code" : progGroups.group("code"),
			})

	infomation = {
		"documents" : documents,
		"title" : unicode(rowMap[r"Opgavetitel"].find("span").text),
		"group_assignment" : group_assignment,
		"members" : members,
		"note" : unicode(rowMap[u"Opgavenote"].text),
		"team" : teams,
		"grading_scale" : "7-step" if rowMap[u"Karakterskala"].text == "7-trinsskala" else "13-step",
		"teachers" : teachers,
		"student_time" : rowMap[u"Elevtid"].text.replace(",", ".").replace("timer", ""),
		"date" : date,
		"in_instruction_detail" : True if rowMap[u"Iundervisningsbeskrivelse"].text == "Ja" else False,
		"uploads" : uploads,
		"group" : {
			"available_students" : availableStudents
		},
		"student" : studentData
	}

	#Delivered by, grade, grade_note, student_note, ended, awaiting, uploaded-documents

	return {
		"status" : "ok",
		"information" : infomation
	}