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

def messages_headers ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/beskeder2.aspx?type=liste&elevid=%s" % ( str(config["school_id"]), str(config["student_id"]) )

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

	response = proxy.session.get(url, data=settings, headers=headers)

	html = response.text

	soup = Soup(html)

	if soup.find("div", attrs={"id" : "s_m_Content_Content_ThreadListPanel"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	headers = soup.findAll("a", attrs={"class": "s_m_Content_Content_ListGridSelectionTree_0"})

	indices = 0, 1, 2, 3, 4, 5, 6
	headers = [i for j, i in enumerate(headers) if j not in indices]

	typeName = "team"

	teams = []
	build_in_groups = []
	own_groups = []

	pageIdProg = re.compile(r"javascript:__doPostBack\('__Page','TREECLICKED_(?P<page_id>.*)'\)")

	for header in headers:
		text = header.text.strip()
		include = True

		if text == "Indbyggede grupper":
			typeName = "build_in_groups"
			include = False
		elif text == "Egne grupper":
			typeName = "own_groups"
			include = False

		if include is True:
			pageGroups = pageIdProg.match(header["href"])
			data = {
				"name" : unicode(text),
				"message_page_id" : pageGroups.group("page_id") if not pageGroups is None else ""
			}

			if typeName == "team":
				teams.append(data)
			elif typeName == "own_groups":
				own_groups.append(data)
			else:
				build_in_groups.append(data)

	return {
		"status" : "ok",
		"teams" : teams,
		"build_in_groups" : build_in_groups,
		"own_groups" : own_groups
	}

#TEST PAGES WITH ALOT OF MESSAGES
def messages ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/beskeder2.aspx?type=liste&elevid=%s" % ( str(config["school_id"]), str(config["student_id"]) )

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

	viewStateX = soup.find("input", attrs={"id" : "__VIEWSTATEX"})["value"]

	settings = {
		"__EVENTTARGET" : "__Page",
		"__EVENTARGUMENT" : "TREECLICKED_%s" % ( str(config["page_id"]) ),
		"__VIEWSTATEX" : viewStateX,
		#"s_m_Content_Content_ListGridSelectionTree_ExpandState" : "nnnnnnennnnnnnnnnnennenn",
		"s_m_Content_Content_ListGridSelectionTree_SelectedNode" : "s_m_Content_Content_ListGridSelectionTreet8",
		"s_m_Content_Content_ListGridSelectionTree_PopulateLog" : "",
		"s$m$Content$Content$MarkChkDD" : "-1"
	}

	response = proxy.session.post(url, data=settings, headers=headers)

	html = response.text

	soup = Soup(html)

	if soup.find("div", attrs={"id" : "s_m_Content_Content_ThreadListPanel"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_threadGV_ctl00"}).findAll("tr")
	if len(rows[0].findAll("td")) > 3 and not rows[0].findAll("td")[3].find("a") is None:
		viewStateKey = soup.find("input", attrs={"id" : "__VIEWSTATEY_KEY"})["value"]
		target = rows[0].findAll("td")[3].find("a")["href"]

		targetProg = re.compile(r'javascript:WebForm_DoPostBackWithOptions\(new WebForm_PostBackOptions\("(?P<target>.*)", "", true, "", "", false, true\)\)')
		targetGroups = targetProg.match(target)

		if targetGroups is None:
			return {
				"status" : False,
				"error" : "Missing target"
			}

		settings = {
			"__EVENTTARGET" : targetGroups.group("target"),
			"__EVENTARGUMENT" : "TREECLICKED_%s" % ( str(config["page_id"]) ),
			"__VIEWSTATEY_KEY" : viewStateKey,
			"s_m_Content_Content_ListGridSelectionTree_ExpandState" : "nnnnnnennnnnnnnnnnennenn",
			"s_m_Content_Content_ListGridSelectionTree_SelectedNode" : "s_m_Content_Content_ListGridSelectionTreet8",
			"s_m_Content_Content_ListGridSelectionTree_PopulateLog" : "",
			"s$m$Content$Content$MarkChkDD" : "-1"
		}

		response = proxy.session.post(url, data=settings, headers=headers)

		html = response.text

		soup = Soup(html)

	if soup.find("div", attrs={"id" : "s_m_Content_Content_ThreadListPanel"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	if soup.find("table", attrs={"id" : "s_m_Content_Content_threadGV_ctl00"}) is None:
		return {
			"status" : "ok",
			"messages" : []
		}

	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_threadGV_ctl00"}).findAll("tr")
	rows.pop(0)

	messages = []

	today = datetime.now()
	shortDayTimeProg = re.compile(r"(?P<day_name>.*) (?P<hour>.*):(?P<minute>.*)")
	timeProg = re.compile(r"(?P<hour>.*):(?P<minute>.*)") # Current day, month, year
	dayProg = re.compile(r"(?P<day_name>.*) (?P<day>.*)/(?P<month>.*)") # Current year
	dateProg = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*)")

	studentProg = re.compile(r"(?P<name>.*) \((?P<class_name>.*)\)")
	teacherProg = re.compile(r"(?P<name>.*) \((?P<abbrevation>.*)\)")

	messageIdProg = re.compile(r"__doPostBack\('__Page','\$LB2\$_MC_\$_(?P<message_id>.*)'\); return false;")

	shownIn = []

	shownInMappings = {
		"-40" : "all_unread",
		"-50" : "all_with_flag",
		"-70" : "newest",
		"-60" : "all_deleted",
		"-10" : "own_messages",
		"-80" : "sent_messages",
		"-20" : "teams",
		"-30" : "build_in_groups",
		"-35" : "own_groups"
	}

	dayConversion = {
		u"Ma" : "Mon",
		u"Ti" : "Tue",
		u"On" : "Wed",
		u"To" : "Thu",
		u"Fr" : "Fri",
		u"Lø" : "Sat",
		u"Sø" : "Son"
	}

	if str(config["page_id"]) in shownInMappings:
		shownIn.append(shownInMappings[str(config["page_id"])])
	else:
		shownIn.append(str(config["page_id"]))

	for row in rows:
		elements = row.findAll("td")
		if not elements is None and len(elements) > 0 and not elements[1].find("img") is None:
			flagOn = True if elements[1].find("img")["src"] == "/lectio/img/flagon.gif" else False
			read = False if elements[2].find("img")["src"] == "/lectio/img/munread.gif" else True
			subject = unicode(elements[3].find("a").text)
			documentsAttached = True if not elements[3].find("img") is None else False
			deleted = True if elements[8].find("img")["src"] == "/lectio/img/add.auto" else False

			date = None

			messageGroups = messageIdProg.match(elements[3].find("a")["onclick"])
			message_id = messageGroups.group("message_id") if not messageGroups is None else ""

			if shortDayTimeProg.match(elements[7].text):
				timeGroups = shortDayTimeProg.match(elements[7].text)
				date = datetime.strptime("%s/%s-%s %s:%s" % (dayConversion[unicode(timeGroups.group("day_name").capitalize())], today.strftime("%W"), today.strftime("%Y"), timeGroups.group("hour"), timeGroups.group("minute")), "%a/%W-%Y %H:%M")
			elif timeProg.match(elements[7].text):
				timeGroups = timeProg.match(elements[7].text)
				date = datetime.strptime("%s/%s-%s %s:%s" % (today.strftime("%d"), today.strftime("%m"), today.strftime("%Y"), timeGroups.group("hour"), timeGroups.group("minute")), "%d/%m-%Y %H:%M")
			elif dayProg.match(elements[7].text):
				dayGroups = dayProg.match(elements[7].text)
				date = datetime.strptime("%s/%s-%s %s:%s" % (dayGroups.group("day"), dayGroups.group("month"), today.strftime("%Y"), "12", "00"), "%d/%m-%Y %H:%M")
			elif dateProg.match(elements[7].text):
				dateGroups = dateProg.match(elements[7].text)
				date = datetime.strptime("%s/%s-%s %s:%s" % (dateGroups.group("day"), dateGroups.group("month"), dateGroups.group("year"), "12", "00"), "%d/%m-%Y %H:%M")

			lastSenderType = "teacher" if elements[4].find("img")["src"] == "/lectio/img/teacher.auto" else "student"
			firstSenderType = "teacher" if elements[5].find("img")["src"] == "/lectio/img/teacher.auto" else "student"
			recipientsType = "student" if elements[6].find("img")["src"] == "/lectio/img/student.auto" else "teacher" if elements[6].find("img")["src"] == "/lectio/img/teacher.auto" else "class"

			lastSender = {}
			firstSender = {}

			if lastSenderType == "teacher":
				teacherGroups = teacherProg.match(elements[4].find("span")["title"])
				lastSender["name"] = unicode(teacherGroups.group("name")) if not teacherGroups is None else ""
				lastSender["abbrevation"] = unicode(teacherGroups.group("abbrevation")) if not teacherGroups is None else ""
			else:
				studentGroups = studentProg.match(elements[4].find("span")["title"])
				lastSender["name"] = unicode(studentGroups.group("name")) if not studentGroups is None else ""
				lastSender["class_name"] = unicode(studentGroups.group("class_name")) if not studentGroups is None else ""

			if firstSenderType == "teacher":
				teacherGroups = teacherProg.match(elements[5].find("span")["title"])
				firstSender["name"] = unicode(teacherGroups.group("name")) if not teacherGroups is None else ""
				firstSender["abbrevation"] = unicode(teacherGroups.group("abbrevation")) if not teacherGroups is None else ""
			else:
				studentGroups = studentProg.match(elements[5].find("span")["title"])
				firstSender["name"] = unicode(studentGroups.group("name")) if not studentGroups is None else ""
				firstSender["class_name"] = unicode(studentGroups.group("class_name")) if not studentGroups is None else ""

			messages.append({
				"flagged" : flagOn,
				"read" : read,
				"documents_attached" : documentsAttached,
				"subject" : subject,
				"last_message" : {
					"sender_user_type" : lastSenderType,
					"sender" : lastSender
				},
				"first_message" : {
					"sender_user_type" : firstSenderType,
					"sender" : firstSender
				},
				"recipients" : {
					"type" : recipientsType
				},
				"changed" : date,
				"thread_id" : message_id,
				"shown_in" : shownIn,
				"deleted" : deleted
			})

	return {
		"status" : "ok",
		"messages" : messages
	}