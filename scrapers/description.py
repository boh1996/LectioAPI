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

def description ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/studieplan/hold_undervisningsbeskrivelse.aspx?holdelementid=%s" % ( str(config["school_id"]), str(config["team_element_id"]) )

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

	if soup.find("div", attrs={"id" : "s_m_Content_Content_holduvb_UvbHoldRepeater_ctl00_uvbCtrl_uvbcontainer"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	tables = soup.find("div", attrs={"id" : "s_m_Content_Content_holduvb_UvbHoldRepeater_ctl00_uvbCtrl_uvbcontainer"}).findAll("table", attrs={"class" : "list"})

	informationElements = tables[0].findAll("td")
	subjectProg = re.compile(r"(?P<subject>.*) (?P<level>.*)$")
	teachers = []
	teamProg = re.compile(r"(?P<team>.*) \((?P<teams>.*)\)")
	teamGroups = teamProg.match(informationElements[9].text.replace("\n", ""))
	teams = []

	if not teamGroups is None:
		teams = teamGroups.group("teams").replace("\n", "").split(", ")

	for row in informationElements[7].findAll("span"):
		teachers.append(unicode(row.text))

	subjectGroups = subjectProg.match(informationElements[5].text.replace("\n", ""))
	terms = informationElements[1].text.replace("\n", "").split(" - ")

	information = {
		"teachers" : teachers,
		"terms" : terms,
		"teams" : teams,
		"team_name" : teamGroups.group("team") if not teamGroups is None else "",
		"subject" : {
			"name" : unicode(subjectGroups.group("subject")) if not subjectGroups is None else unicode(informationElements[5].text),
			"level" : subjectGroups.group("level") if not subjectGroups is None else ""
		},
		"institution" : unicode(informationElements[3].text.replace("\n", "")),
	}

	tables.pop(0)
	tables.pop(0)

	phases = []
	phaseIdProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/studieplan\/forloeb_vis.aspx\?phaseid=(?P<phase_id>.*)&prevurl=(?P<prev_url>.*)")
	coversProg = re.compile(ur"Anvendt modullængden (?P<length>.*) (?P<type>.*)\. fra skoleåret (?P<term>.*)")

	for table in tables:
		if not table is None:
			rows = table.findAll("tr", recursive=False)
			elements = []

			for row in rows:
				elements = elements + row.findAll("td", recursive=False)

			if not elements[1].find("a") is None:
				phaseIdGroups = phaseIdProg.match(elements[1].find("a")["href"])
				reachSpans = elements[5].findAll("span")
				title = reachSpans[2]["title"] if "title" in reachSpans[2] else reachSpans[2].text
				coversGroups = coversProg.match(title)
				focusPoints = []
				focusRows = elements[7].find("ul").findAll("li", recursive=False)
				descriptionText = elements[1].find("span").text

				if len(focusRows) > 0:
					for row in focusRows:
						header = unicode(row.text)
						focusPointElements = []
						if row.find_next().name == "ul":
							for focusElement in row.find_next().findAll("li"):
								focusPointElements.append(unicode(focusElement.text))

						focusPoints.append({
							"header" : header,
							"elements" : focusPointElements
						})

				work_methods = []

				for row in elements[9].findAll("li"):
					work_methods.append(unicode(row.text.replace("\t", "").replace("\n", "").replace("\r", "")))

				readings = []
				if not elements[3].find("span").find("i") is None:
					elements[3].find("span").find("i").decompose()
					for row in elements[3].find("span").findAll("br"):
						text = unicode(row.find_next(text=True).string).encode("utf8")
						readings.append({"text" : text})

				elements[3].find("span").decompose()
				links = []

				for link in elements[3].findAll("a"):
					links.append({
						"href" : link["href"],
						"text" : unicode(link.find_next(text=True).find_next(text=True)[3:].replace("\t", "").replace("\r\n", ""))
					})
					link.find_next(text=True).find_next(text=True).extract()
					link.decompose()

				written = []

				if not elements[3].find("table") is None:
					writtenRows = elements[3].findAll("tr")
					writtenRows.pop(0)

					for row in writtenRows:
						writtenRowElements = row.findAll("td")
						written.append({
							"title" : writtenRowElements[0].text.replace("\r\n", "").replace("\t", ""),
							"date" : datetime.strptime(writtenRowElements[1].text.replace("\r\n", "").replace("\t", "").strip(), "%d-%m-%Y")
						})

					elements[3].find("table").decompose()

				for x in elements[3].findAll("i"):
					x.decompose()

				documents = []

				for row in elements[3].findAll(text=True):
					if len(row) > 1:
						documents.append({
							"name" : row.strip().replace("\r\n", "").replace("\t", "")
						})

				phases.append({
					"reach" : {
						"estimate" : "unknown" if reachSpans[0].text == "Ikke angivet" else reachSpans[0].text.replace(",", ".").replace(" moduler", "").strip(),
						"covers" : {
							"length" : "unknown" if reachSpans[1].text == "Ikke angivet" else reachSpans[1].text.replace(" moduler", ""),
							"type" : "modules"
						},
						"details" : {
							"length" : coversGroups.group("length") if not coversGroups is None else "45",
							"type" : coversGroups.group("type") if not coversGroups is None else "min",
							"term" : "20" + coversGroups.group("term") if not coversGroups is None else soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
						}
					},
					"methods" : work_methods,
					"name" : unicode(elements[1].find("a").text),
					"phase_id" : phaseIdGroups.group("phase_id") if not phaseIdGroups is None else "",
					"focus_points" : focusPoints,
					"readings" : readings,
					"links" : links,
					"documents" : documents,
					"written" : written,
					"description" : descriptionText
				})

	return {
		"status" : "ok",
		"information" : information,
		"phases" : phases,
		"term" : {
			"value" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
			"years_string" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
		}
	}