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
import authenticate

def exams ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/proevehold.aspx?type=elev&studentid=%s" % ( str(config["school_id"]), str(config["student_id"]))

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

	if soup.find("div", attrs={"id" : "m_Content_LectioDetailIslandProevehold_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	exams = []
	tables = soup.find("div", attrs={"id" : "m_Content_LectioDetailIslandProevehold_pa"}).findAll("table")
	informationRows = tables[0].findAll("td")

	classProg = re.compile(r"(?P<class_name>.*) (?P<student_class_id>.*)")
	classGroups = classProg.match(informationRows[1].text)

	information = {
		"name" : unicode(informationRows[3].text),
		"student_class_id_full" : informationRows[1].text,
		"base_class" : informationRows[5].text,
		"class_name" : classGroups.group("class_name") if not classGroups is None else "",
		"student_class_id" : classGroups.group("student_class_id") if not classGroups is None else "",
	}

	return {
		"status" : "ok",
		"exams" : exams,
		"information" : information
	}