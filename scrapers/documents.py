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
import os.path
import context_card

def document ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/dokumentrediger.aspx?dokumentid=%s" % ( str(config["school_id"]), str(config["document_id"]) )

	if session is False:
		session = authenticate.authenticate(config)

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

	if soup.find("div", attrs={"id" : "m_Content_Dokument_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	elements = soup.find("div", attrs={"id" : "m_Content_Dokument_pa"}).findAll("td")

	creator = context_card.user({
		"context_card_id" : elements[3].find("span")["lectiocontextcard"],
		"school_id" : config["school_id"]
	}, session)["user"]

	changer = elements[4].find("span")["lectiocontextcard"]
	elements[4].find("span").decompose()
	dateText = elements[4].text.replace(" af ", "").strip()
	dateTimeProg = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*)")
	dateGroups = dateTimeProg.match(dateText)
	date = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""

	document = {
		"name" : unicode(elements[0].find("a").text).replace("\t", "").replace("\n", "").replace("\r", "").strip(),
		"extension" : os.path.splitext(elements[0].find("a").text.replace("\t", "").replace("\n", "").replace("\r", "").strip())[1].replace(".", ""),
		"size" : elements[2].text.replace(",", ".").replace("\t", "").replace("\n", "").replace("\r", "").strip(),
		"document_id" : str(config["document_id"]),
		"creator" : creator,
		"changer" : {
			"context_card_id" : changer,
			"type" : "teacher" if "T" in changer else "student",
			"date" : date
		},
		"comment" : soup.find("textarea", attrs={"id" : "m_Content_EditDocComments_tb"}).text.replace("\r\n",""),
		"public" : True if "checked" in soup.find("input", attrs={"id" : "m_Content_EditDocIsPublic"}).attrs else False
	}

	return {
		"status" : "ok",
		"document" : document
	}

def folders ( config, session = False ):
	if session is False:
		session = authenticate.authenticate(config)

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

	url = "https://www.lectio.dk/lectio/%s/DokumentOversigt.aspx?elevid=%s" %( str(config["school_id"]), str(config["student_id"]) )

	response = proxy.session.get(url, headers=headers)

	html = response.text

	soup = Soup(html)

	if soup.find("div", attrs={"id" : "s_m_Content_Content_FolderTreeView"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	folders = []

def documents ( config, session = False ):
	if session is False:
		session = authenticate.authenticate(config)

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

	url = "https://www.lectio.dk/lectio/%s/DokumentOversigt.aspx?elevid=%s&folderid=%s" %( str(config["school_id"]), str(config["student_id"]), str(config["folder_id"]) )

	response = proxy.session.get(url, headers=headers)

	html = response.text

	soup = Soup(html)

	if soup.find("table", attrs={"id" : "s_m_Content_Content_DocumentGridView_ctl00"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_DocumentGridView_ctl00"}).findAll("tr")
	rows.pop(0)

	shortDayTimeProg = re.compile(r"(?P<day_name>.*) (?P<hour>.*):(?P<minute>.*)")
	timeProg = re.compile(r"(?P<hour>.*):(?P<minute>.*)") # Current day, month, year
	dayProg = re.compile(r"(?P<day_name>.*) (?P<day>.*)/(?P<month>.*)") # Current year
	dateProg = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*)")

	dayConversion = {
		u"Ma" : "Mon",
		u"Ti" : "Tue",
		u"On" : "Wed",
		u"To" : "Thu",
		u"Fr" : "Fri",
		u"Lø" : "Sat",
		u"Sø" : "Son"
	}

	documents = []
	documentIdProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/dokumenthent.aspx\?documentid=(?P<document_id>.*)")

	for row in rows:
		elements = row.findAll("td")
		idGroups = documentIdProg.match(elements[1].find("a")["href"])

		changer = context_card.user({
			"context_card_id" : elements[3]["lectiocontextcard"],
			"school_id" : config["school_id"]
		}, session)

		if shortDayTimeProg.match(elements[4].text):
			timeGroups = shortDayTimeProg.match(elements[4].text)
			date = datetime.strptime("%s/%s-%s %s:%s" % (dayConversion[unicode(timeGroups.group("day_name").capitalize())], today.strftime("%W"), today.strftime("%Y"), timeGroups.group("hour"), timeGroups.group("minute")), "%a/%W-%Y %H:%M")
		elif timeProg.match(elements[4].text):
			timeGroups = timeProg.match(elements[4].text)
			date = datetime.strptime("%s/%s-%s %s:%s" % (today.strftime("%d"), today.strftime("%m"), today.strftime("%Y"), timeGroups.group("hour"), timeGroups.group("minute")), "%d/%m-%Y %H:%M")
		elif dayProg.match(elements[4].text):
			dayGroups = dayProg.match(elements[4].text)
			date = datetime.strptime("%s/%s-%s %s:%s" % (dayGroups.group("day"), dayGroups.group("month"), today.strftime("%Y"), "12", "00"), "%d/%m-%Y %H:%M")
		elif dateProg.match(elements[4].text):
			dateGroups = dateProg.match(elements[4].text)
			date = datetime.strptime("%s/%s-%s %s:%s" % (dateGroups.group("day"), dateGroups.group("month"), dateGroups.group("year"), "12", "00"), "%d/%m-%Y %H:%M")

		data = {
			"folder_id" : str(config["folder_id"]),
			"name" : unicode(elements[1].find("span")["title"].replace("Fulde filnavn: ", "")),
			"extension" : os.path.splitext(elements[1].find("span")["title"].replace("Fulde filnavn: ", ""))[1].replace(".", ""),
			"comment" : unicode(elements[2].find("span").text),
			"document_id" : idGroups.group("document_id") if not idGroups is None else "",
			"size" : elements[5].text.replace(",", "."),
			"date" : date,
			"user" : changer["user"]
		}

		documents.append(data)

	return {
		"status" : "ok",
		"documents" : documents
	}