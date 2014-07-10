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

def phase ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/studieplan/forloeb_vis.aspx?phaseid=%s" % ( str(config["school_id"]), str(config["phase_id"]) )

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

	if soup.find("div", attrs={"id" : "m_Content_islandViewForløb_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	headers = []
	elements = []

	for row in soup.find("div", attrs={"id" : "m_Content_islandViewForløb_pa"}).find("table").findAll("tr", recursive=False):
		headers.append(row.find("th", recursive=False))
		elements.append(row.find("td", recursive=False))

	rows = functions.mapRows(headers, elements)

	changeProg = re.compile(r"(?P<date>.*) af (?P<teacher>.*) \((?P<abbrevation>.*)\)")
	teamProg = re.compile(ur"(?P<term>.*): (?P<team>.*)")

	teams = []
	periods = []
	focusPoints = []
	workMethods = []
	activities = []
	assignments = []

	periodeProg = re.compile(r"(?P<start>.*)	-	(?P<end>.*)")
	activityProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/aktivitet\/aktivitetinfo.aspx\?id=(?P<activity_id>.*)&prevurl=(?P<prev_url>.*)")

	if not rows["Aktiviteter"].find(attrs={"id" : "m_Content_ActivitiesGV"}) is None:
		for row in rows["Aktiviteter"].find(attrs={"id" : "m_Content_ActivitiesGV"}).findAll("tr")[1:]:
			elements = row.findAll("td")
			activityGroups = activityProg.match(elements[1].find("a")["href"])
			activities.append({
				"activity_id" : activityGroups.group("activity_id") if not activityGroups is None else ""
			})

	if not rows["Skriftligtarbejde"].find(attrs={"id" : "m_Content_ExercisesGrid"}) is None:
		for row in rows["Skriftligtarbejde"].find(attrs={"id" : "m_Content_ExercisesGrid"}).findAll("tr")[1:]:
			elements = row.findAll("td")

			assignments.append({
				"name" : unicode(elements[0].text),
				"date" : datetime.strptime(elements[1].text.strip(), "%d-%m-%Y")
			})

	for row in rows["Periode(r)"].text.strip().replace("\r\n", "").split("\n"):
		periodeGroups = periodeProg.match(row)

		periods.append({
			"start" : datetime.strptime(periodeGroups.group("start").strip(), "%d-%m-%Y") if not periodeGroups is None else "",
			"end" : datetime.strptime(periodeGroups.group("end").strip(), "%d-%m-%Y") if not periodeGroups is None else ""
		})

	for row in rows["Arbejdsformer"].findAll("span"):
		workMethods.append({
			"text" : unicode(functions.cleanText(row.text))
		})

	termProg = re.compile(r"(?P<value>.*)\/(?P<end>.*)")

	for row in rows["Hold"].findAll("span"):
		teamGroups = teamProg.match(row.text)
		termGroups = termProg.match(teamGroups.group("term") if not teamGroups is None else "")
		teams.append({
			"context_card_id" : row["lectiocontextcard"],
			"team_element_id" : row["lectiocontextcard"].replace("HE", ""),
			"name" : teamGroups.group("team") if not teamGroups is None else "",
			"term" : {
				"years_string" : teamGroups.group("term") if not teamGroups is None else "",
				"value" : termGroups.group("value") if not termGroups is None else ""
			}
		})

	if not rows["Saerligefokuspunkter"].find("ul") is None:
		focusRows = rows["Saerligefokuspunkter"].find("ul").findAll("li", recursive=False)

		if len(focusRows) > 0:
			for row in focusRows:
				header = unicode(row.text)
				focusPointElements = []
				if row.find_next().name == "ul":
					for focusElement in row.find_next().findAll("li"):
						focusPointElements.append(focusElement.text.encode("utf8"))

				focusPoints.append({
					"header" : header,
					"elements" : focusPointElements
				})

	changedGroups = changeProg.match(rows["Sidstaendret"].text.strip().replace("\r\n", "").replace("\t", ""))
	createdGroups = changeProg.match(rows["Oprettet"].text.strip().replace("\r\n", "").replace("\t", ""))

	estimate = rows["Estimat"].text.strip().replace("\r\n", "").replace("\t", "").replace(" moduler", "").replace(",", ".")

	information = {
		"title" : rows["Titel"].text.strip().replace("\r\n", "").replace("\t", "").encode("utf8"),
		"note" : rows["Note"].text.strip().replace("\r\n", "").replace("\t", "").encode("utf8"),
		"estimate" : {
			"type" : "modules",
			"length" : "none" if estimate == "ingen" else estimate
		},
		"changed" : {
			"date" : datetime.strptime(changedGroups.group("date"), "%d/%m-%Y") if not changedGroups is None else "",
			"teacher" : {
				"name" : unicode(changedGroups.group("teacher")) if not changedGroups is None else "",
				"abbrevation" : unicode(changedGroups.group("abbrevation")) if not changedGroups is None else ""
			}
		},
		"teams" : teams,
		"created" : {
			"date" : datetime.strptime(createdGroups.group("date"), "%d/%m-%Y") if not createdGroups is None else "",
			"teacher" : {
				"name" : unicode(createdGroups.group("teacher")) if not createdGroups is None else "",
				"abbrevation" : unicode(createdGroups.group("abbrevation")) if not createdGroups is None else ""
			}
		},
		"periods" : periods,
		"focus_points" : focusPoints,
		"methods" : workMethods,
		"activities" : activities,
		"assignments" : assignments
	}

	return {
		"status" : "ok",
		"phase" : information
	}