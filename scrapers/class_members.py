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
from pytz import timezone
import authenticate

def class_members ( config, session = False ):
	if session == False:
		url = "https://www.lectio.dk/lectio/%s/subnav/members.aspx?klasseid=%s&showteachers=1&showstudents=1&reporttype=std" % ( str(config["school_id"]), str(config["class_id"]) )
		cookies = {}
	else:
		session = authenticate.authenticate(config)
		url = "https://www.lectio.dk/lectio/%s/subnav/members.aspx?klasseid=%s&showteachers=1&showstudents=1" % ( str(config["school_id"]), str(config["class_id"]) )
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

	if soup.find("table", attrs={"id" : "s_m_Content_Content_laerereleverpanel_alm_gv"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_laerereleverpanel_alm_gv"}).findAll("tr")
	headers = rows[0].findAll("th")
	rows.pop(0)

	teachers = []
	students = []
	pictureOffset = 1 if len(headers) == 7 else 0
	pictureProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/GetImage.aspx\?pictureid=(?P<picture_id>.*)")

	if len(rows) > 0:
		for row in rows:
			elements = row.findAll("td")
			personType = "teacher" if unicode(elements[0 + pictureOffset].text) == u"Lærer" else "student"
			data = {
				"type" : personType,
				"first_name" : unicode(elements[2 + pictureOffset].find("a").text),
				"person_text_id" : elements[1 + pictureOffset].find("span").text,
				"last_name" : unicode(elements[3 + pictureOffset].find("span").text),
				"full_name" : unicode(elements[2 + pictureOffset].find("a").text) + " " + unicode(elements[3 + pictureOffset].find("span").text),
				"person_id" : elements[1 + pictureOffset]["lectiocontextcard"].replace("T", "") if personType == "teacher" else elements[1 + pictureOffset]["lectiocontextcard"].replace("S", ""),
				"context_card_id" : elements[1 + pictureOffset]["lectiocontextcard"]
			}
			if pictureOffset == 1:
				pictureGroups = pictureProg.match(elements[0].find("img")["src"])
				data ["picture_id"] = pictureGroups.group("picture_id") if not pictureGroups is None else ""

			if personType == "teacher":
				data["teams"] = elements[5 + pictureOffset].text.split(", ")
				teachers.append(data)
			else:
				data["field_of_study"] = {
					"name" : unicode(elements[4 + pictureOffset].find("span").text),
					"context_card_id" : elements[4 + pictureOffset].find("span")["lectiocontextcard"],
					"field_of_study_id" : elements[4 + pictureOffset].find("span")["lectiocontextcard"].replace("SR", "")
				}
				students.append(data)

	return {
		"status" : "ok",
		"teachers" : teachers,
		"students" : students
	}