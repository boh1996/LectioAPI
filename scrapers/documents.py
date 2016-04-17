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

teamCache = {}

folderIdProg = re.compile(r"javascript:__doPostBack\('__Page','TREECLICKED_(?P<folder_id>.*)'\)")

studentFolderProg = re.compile(r"S(?P<student_id>.*)_(?P<folder_name>.*)")
studentSubFolderProg = re.compile(r"S(?P<student_id>.*)_FS(?P<subfolder_id>.*)_")
teamFolderProg = re.compile(r"H(?P<team_id>.*)__")
teamSubFolderProg = re.compile(r"H(?P<team_id>.*)_FH(?P<subfolder_id>.*)_")
topType = "folder"

def match_folder ( folder_id, session, config, type ):
	if studentSubFolderProg.match(folder_id):
		groups = studentSubFolderProg.match(folder_id)
		return {
			"type" : "student_sub_folder",
			"student_id" : groups.group("student_id").replace("_", ""),
			"subfolder_id" : groups.group("subfolder_id")
		}
	elif studentFolderProg.match(folder_id):
		groups = studentFolderProg.match(folder_id)
		return {
			"type" : "student_folder",
			"folder_name" : groups.group("folder_name").replace("_", ""),
			"student_id" : groups.group("student_id").replace("_", ""),
		}
	elif teamSubFolderProg.match(folder_id):
		groups = teamSubFolderProg.match(folder_id)
		data = {
			"type" : "team_sub_folder",
			"team_id" : groups.group("team_id").replace("_", ""),
			"subfolder_id" : groups.group("subfolder_id").replace("_", "")
		}
		if type == "folder":
			if not groups.group("team_id").replace("_", "") in teamCache:
				team = context_card.team({"school_id" : str(config["school_id"]), "context_card_id" : "H" + groups.group("team_id").replace("_", "")}, session)
				teamCache[groups.group("team_id").replace("_", "")] = team
			else:
				team = teamCache[groups.group("team_id").replace("_", "")]

			data["team"] = team["team"]
		return data
	elif teamFolderProg.match(folder_id):
		groups = teamFolderProg.match(folder_id)
		data = {
			"type" : "team_folder",
			"team_id" : groups.group("team_id").replace("_", "")
		}
		if type == "folder":
			if not groups.group("team_id").replace("_", "") in teamCache:
				team = context_card.team({"school_id" : str(config["school_id"]), "context_card_id" : "H" + groups.group("team_id").replace("_", "")}, session)
				teamCache[groups.group("team_id").replace("_", "")] = team
			else:
				team = teamCache[groups.group("team_id").replace("_", "")]
			data["team"] = team["team"]
		return data
	else:
		return {
			"type" : "other"
		}

def find_folders ( container, parent = False, session = False, config = None ):
	global topType
	mappings = {
		u"Nyeste" : u"newest",
		u"Egne dokumenter" : u"own_documents",
		u"Hold" : u"teams",
		u"Indbyggede grupper" : u"build_in_groups",
		u"Egne grupper" : u"own_groups"
	}

	tables = container.findAll("table", recursive=False)

	folders = []

	for table in tables:
		elements = table.findAll("td")
		nameText = ""
		if "rel" in elements[len(elements)-1].find("a").attrs:
			nameText = unicode(elements[len(elements)-1].find("a")["rel"]).replace("Mappenavn: ", "")
		elif "title" in elements[len(elements)-1].find("a").attrs:
			nameText = unicode(elements[len(elements)-1].find("a")["title"]).replace("Mappenavn: ", "")

		if u"Autogenereret indhold" in nameText or nameText == u"":
			nameText = unicode(elements[len(elements)-1].text)

		nameText = unicode(nameText.replace("\n", ""))

		name = mappings[nameText] if nameText in mappings else nameText
		idGroups = folderIdProg.match(elements[len(elements)-1].find("a")["href"])
		folder_id = idGroups.group("folder_id") if not idGroups is None else ""
		data = {
			"name" : name,
			"folder_id" : folder_id,
			"type" : "folder"
		}

		if name == u"Lektioner":
			data["type"] = "lessons"
		elif not name == nameText:
			data["type"] = "build_in"
			if not nameText == u"Hold":
				topType = "build_in"
			else:
				topType = "user"
		else:
			data["type"] = "folder"

		if topType == "build_in":
			data["type"] = topType

		if not parent is False:
			data["parent_id"] = parent

		data["folder"] = match_folder(folder_id, session, config, data["type"])

		folders.append(data)

		if not elements[len(elements)-3].find("a") is None:
			folders = folders + find_folders(container.find("div", attrs={"id" : elements[len(elements)-3].find("a")["id"] + "Nodes"}), folder_id, session, config)

	return folders

def document ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/dokumentrediger.aspx?dokumentid=%s" % ( str(config["school_id"]), str(config["document_id"]) )

	if session is False:
		session = authenticate.authenticate(config)

	if session == False:
		return {"status" : "error", "type" : "authenticate"}

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

	offset = 0

	elements = soup.find("div", attrs={"id" : "m_Content_Dokument_pa"}).findAll("td")

	if len(elements) < 7:
		offset = 1

	creator = context_card.user({
		"context_card_id" : elements[3-offset].find("span")["lectiocontextcard"],
		"school_id" : config["school_id"]
	}, session)["user"]

	changer = elements[4-offset].find("span")["lectiocontextcard"]
	elements[4-offset].find("span").decompose()
	dateText = elements[4-offset].text.replace(" af ", "").strip()
	dateTimeProg = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*)")
	dateGroups = dateTimeProg.match(dateText)
	date = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""

	connectionRows = soup.find("table", attrs={"id" : "m_Content_AffiliationsGV"}).findAll("tr")
	connectionRows.pop(0)

	connections = []

	for row in connectionRows:
		rowElements = row.findAll("td")

		data = {
			"context_card_id" : rowElements[0]["lectiocontextcard"],
			"type" : "team" if "H" in rowElements[0]["lectiocontextcard"] else "teacher" if "T" in rowElements[0]["lectiocontextcard"] else "student",
			"name" : unicode(rowElements[0].find("span").text),
			"can_edit" : True if "checked" in rowElements[1].find("input").attrs else False
		}

		if rowElements[2].find("select"):
			folder_id = rowElements[2].find("select").select('option[selected="selected"]')[0]["value"]
			data["folder_id"] = folder_id

		connections.append(data)

	document = {
		"name" : unicode(elements[0].find("a").text).replace("\t", "").replace("\n", "").replace("\r", "").strip(),
		"extension" : os.path.splitext(elements[0].find("a").text.replace("\t", "").replace("\n", "").replace("\r", "").strip())[1].replace(".", ""),
		"size" : elements[2-offset].text.replace(",", ".").replace("\t", "").replace("\n", "").replace("\r", "").strip(),
		"document_id" : str(config["document_id"]),
		"creator" : creator,
		"changer" : {
			"context_card_id" : changer,
			"type" : "teacher" if "T" in changer else "student",
			"date" : date
		},
		"comment" : soup.find("textarea", attrs={"id" : "m_Content_EditDocComments_tb"}).text.replace("\r\n",""),
		"public" : True if "checked" in soup.find("input", attrs={"id" : "m_Content_EditDocIsPublic"}).attrs else False,
		"connections" : connections,
		"term" : {
			"value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
			"years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
		}
	}

	return {
		"status" : "ok",
		"document" : document
	}

def folders ( config, session = False ):
	if session is False:
		session = authenticate.authenticate(config)

	if session == False:
		return {"status" : "error", "type" : "authenticate"}

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

	folders = find_folders(soup.find("div", attrs={"id" : "s_m_Content_Content_FolderTreeView"}), False, session, config)

	return {
		"status" : "ok",
		"folders" : folders
	}

def documents ( config, session = False ):
	if session is False:
		session = authenticate.authenticate(config)

	if session == False:
		return {"status" : "error", "type" : "authenticate"}

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
f = open("log.json", "w")

print >> f, folders({
	"school_id" : 517,
	"student_id" : 4789793691,
	"username" : "boh1996",
	"password" : "jwn53yut",
	"branch_id" : "4733693427"
});
f.close()