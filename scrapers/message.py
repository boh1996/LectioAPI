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
import context_card

def has_colspan ( element ):
	if element is None:
		return False
	elif "colspan" in element.attrs:
		return True

def message ( config, session = False ):
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
		"__EVENTARGUMENT" : "$LB2$_MC_$_%s" % ( str(config["thread_id"]) ),
		"__VIEWSTATEX" : viewStateX,
	}

	response = proxy.session.post(url, data=settings, headers=headers)

	html = response.text

	soup = Soup(html)

	if soup.find("div", attrs={"id" : "s_m_Content_Content_ViewThreadPagePanel"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	flagged = False if soup.find("input", attrs={"id" : "s_m_Content_Content_FlagThisThreadBox"})["src"] == "/lectio/img/flagoff.gif" else True

	originalElements = soup.find("table", attrs={"class" : "ShowMessageRecipients"}).findAll("td")

	originalSenderUser = context_card.user({
		"context_card_id" : originalElements[8].find("span")["lectiocontextcard"],
		"school_id" : config["school_id"]
	}, session)

	originalSenderUser["user"]["user_context_card_id"] = originalElements[8].find("span")["lectiocontextcard"]
	originalSenderUser["user"]["person_id"] = originalElements[8].find("span")["lectiocontextcard"].replace("U", "")

	originalSubject = unicode(functions.cleanText(originalElements[2].text))

	recipients = []

	studentRecipientProg = re.compile(r"(?P<name>.*) \((?P<student_class_id>.*)\)")
	teacherRecipientProg = re.compile(r"(?P<name>.*) \((?P<abbrevation>.*)\)")

	# Fill in the single users, added as recipients
	for row in originalElements[11].findAll("span"):
		context_card_id = row["lectiocontextcard"]
		userType = ""
		data = {
			"context_card_id" : context_card_id
		}

		if "S" in context_card_id:
			userType = "student"
			studentGroups = studentRecipientProg.match(row.text)
			data["person_id"] = context_card_id.replace("S", "")
			data["student_id"] = context_card_id.replace("S", "")
			data["name"] = unicode(studentGroups.group("name")) if not studentGroups is None else ""
			data["student_class_id"] = studentGroups.group("student_class_id") if not studentGroups is None else ""

		elif "T" in context_card_id:
			userType = "teacher"
			teacherGroups = teacherRecipientProg.match(row.text)
			data["person_id"] = context_card_id.replace("T", "")
			data["teacher_id"] = context_card_id.replace("T", "")
			data["abbrevation"] = unicode(teacherGroups.group("abbrevation")) if not teacherGroups is None else ""
			data["name"] = unicode(teacherGroups.group("name")) if not teacherGroups is None else ""

		data["type"] = userType

		recipients.append(data)

		row.decompose()

	recipientRows = originalElements[11].text.split(", ")

	for row in recipientRows:
		text = row.replace("\n", "").replace("\r", "").replace("\t", "")

		if "Holdet" in text:
			text = text.replace("Holdet ", "")

			recipients.append({
				"type" : "team",
				"name" : unicode(text)
			})
		elif "Gruppen" in text:
			text = text.replace("Gruppen ", "")
			recipients.append({
				"type" : "group",
				"name" : unicode(text)
			})

	messages = []

	answerProg = re.compile(r"javascript:__doPostBack\('__Page','ANSWERMESSAGE_(?P<message_id>.*)'\);")
	dateTimeProg = re.compile(r"(?P<day>.*)\/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*)")
	messageLevels = {}

	for row in soup.find("table", attrs={"id" : "s_m_Content_Content_ThreadTable"}).findAll("tr"):
		if not row.find("table") is None:
			level = row.findAll(has_colspan)[0]["colspan"]
			data = {}
			messageDetailElements = row.find("table").findAll("td")

			# Subject
			data["subject"] = unicode(messageDetailElements[0].find("h4").text)
			messageDetailElements[0].find("h4").decompose()

			# Sender
			messageSender = context_card.user({
				"context_card_id" : messageDetailElements[0].find("span")["lectiocontextcard"],
				"school_id" : config["school_id"]
			}, session)

			messageSender["user"]["user_context_card_id"] = originalElements[8].find("span")["lectiocontextcard"]
			messageSender["user"]["person_id"] = originalElements[8].find("span")["lectiocontextcard"].replace("U", "")
			data["sender"] = messageSender["user"]

			messageDetailElements[0].find("span").decompose()

			# Time
			timeText = messageDetailElements[0].text.replace("Af , ", "").strip().replace("\n", "").replace("\t", "")
			dateGroups = dateTimeProg.match(timeText)
			data["date"] = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""

			# Message id
			answerGroups = answerProg.match(messageDetailElements[1].find("button")["onclick"])
			message_id = answerGroups.group("message_id") if not answerGroups is None else ""
			data["message_id"] = message_id

			row.find("table").decompose()

			# Get message text
			data["message"] = unicode(row.text.strip())

			# Get parent
			if str(int(level)+1) in messageLevels:
				data["parrent_id"] = messageLevels[str(int(level)+1)]

			messageLevels[level] = message_id

			messages.append(data)

	messageInfo = {
		"original_subject" : originalSubject,
		"flagged" : flagged,
		"original_sender" : originalSenderUser["user"],
		"recipients" : recipients,
		"messages" : messages
	}

	return {
		"status" : "ok",
		"message" : messageInfo,
	}