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

def outgoing_censor ( config ):
	url = "https://www.lectio.dk/lectio/%s/proevehold.aspx?type=udgcensur&outboundCensorID=%s" % ( str(config["school_id"]), str(config["outgoing_censor_id"]) )

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

	teacherProg = re.compile(r"(?P<name>.*) \((?P<abbrevation>.*)\)")
	teacherGroups = teacherProg.match(soup.find("td", attrs={"id" : "m_Content_outboundcensor_teachername"}).text)
	periodProg = re.compile("(?P<start>.*) - (?P<end>.*)")
	periodGroups = periodProg.match(soup.find(attrs={"id" : "m_Content_outboundcensor_periode"}).text)
	institutionProg = re.compile(r"(?P<institution_id>\d*) (?P<institution>.*)")

	phases = []
	information = {}
	description = False

	phaseIds = {}
	phaseNames = []

	if not soup.find(attrs={"id" : "m_Content_holdUvbCtrl_UvbHoldRepeater_ctl00_uvbCtrl_uvbundervisningsbeskrivelseTypeH"}) is None:
		tables = soup.find(attrs={"id" : "m_Content_holdUvbCtrl_UvbHoldRepeater_ctl00_uvbCtrl_uvbcontainer"}).findAll("table", attrs={"class" : "list"})

		for x in tables[1].findAll("a"):
			phaseIds[x.text] = x["href"].replace("#ph", "")
			phaseNames.append(x.text)

		description = True

		informationElements = tables[0].findAll("td")
		subjectProg = re.compile(r"(?P<subject>.*) (?P<level>.*)$")
		teachers = []
		teamProg = re.compile(r"(?P<team>.*) \((?P<teams>.*)\)")
		teamGroups = teamProg.match(informationElements[9].text.replace("\n", ""))
		teams = []

		if not teamGroups is None:
			teams = []
			for x in teamGroups.group("teams").replace("\n", "").split(", "):
				teams.append({"name" : x})

		for row in informationElements[7].findAll("span"):
			if len(row.text) > 0:
				teachers.append({"name" : row.text})

		subjectGroups = subjectProg.match(informationElements[5].text.replace("\n", ""))
		terms = []

		termProg = re.compile(r"(?P<value>.*)\/(?P<end>.*)")

		for x in informationElements[1].text.replace("\n", "").split(" - "):
			termGroups = termProg.match(x)

			terms.append({
				"value" : termGroups.group("value") if not termGroups is None else "",
				"years_string" : x
			})

		information = {
			"teachers" : teachers,
			"terms" : terms,
			"teams" : teams,
			"team_name" : teamGroups.group("team") if not teamGroups is None else "",
			"subject" : {
				"name" : subjectGroups.group("subject").encode("utf8") if not subjectGroups is None else informationElements[5].text.encode("utf8"),
				"level" : subjectGroups.group("level") if not subjectGroups is None else ""
			},
			"institution" : informationElements[3].text.replace("\n", "").encode("utf8"),
		}

		tables.pop(0)
		tables.pop(0)

		phases = []
		coversProg = re.compile(ur"Anvendt modullængden (?P<length>.*) (?P<type>.*)\. fra skoleåret (?P<term>.*)")

		index = 0

		for table in tables:
			if not table is None:
				index = index + 1
				rows = table.findAll("tr", recursive=False)
				elements = []

				for row in rows:
					elements = elements + row.findAll("td", recursive=False)

				reachSpans = elements[5].findAll("span")
				title = reachSpans[2]["title"] if "title" in reachSpans[2] else reachSpans[2].text
				coversGroups = coversProg.match(title)
				focusPoints = []
				focusRows = []
				if not elements[7].find("ul") is None:
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
						"covers" : {
							"length" : "unknown" if reachSpans[1].text == "Ikke angivet" else reachSpans[1].text.replace(" moduler", ""),
							"type" : "modules"
						},
						"details" : {
							"length" : coversGroups.group("length") if not coversGroups is None else "45",
							"type" : coversGroups.group("type") if not coversGroups is None else "min",
							"term" : "20" + coversGroups.group("term") if not coversGroups is None else soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
						}
					},
					"estimate" : {
						"type" : "modules",
						"length" : "unknown" if reachSpans[0].text == "Ikke angivet" else reachSpans[0].text.replace(",", ".").replace(" moduler", "").strip(),
					},
					"methods" : work_methods,
					"name" : phaseNames[index - 1].encode("utf8"),
					"phase_id" : phaseIds[phaseNames[index - 1]],
					"focus_points" : focusPoints,
					"readings" : readings,
					"links" : links,
					"documents" : documents,
					"written" : written,
					"description" : descriptionText,
					"title" : elements[1].find(text=True).string.replace("\r\n", "").replace("\t", "").encode("utf8")
				})

	institutionGroups = institutionProg.match(soup.find("td", attrs={"id" : "m_Content_outboundcensor_institution"}).text)

	testTeamName = soup.find("td", attrs={"id" : "m_Content_outboundcensor_proeveholdname"}).text
	test_type_code = "other"
	gym_type = "AGYM"
	test_type_team_name = ""

	xprsProg = re.compile(r"(?P<code>.*) (?P<type>.*) (?P<subject_name>.*)")
	xprsGroups = xprsProg.match(soup.find("td", attrs={"id" : "m_Content_outboundcensor_xprsproeve"}).text)
	xprs_type = xprsGroups.group("type") if not xprsGroups is None else ""

	testTypeCodeProg = re.compile(r"(?P<team_name>.*) (?P<code>[\w\S]*)$")
	testTypeCodeGroups = testTypeCodeProg.match(testTeamName)
	testTypeAltCodePRog = re.compile(r"(?P<team_name>.*) (?P<code>[\w\S]*) \((?P<gym_type>[\w\S]*)\)$")
	testTypeCodeAltGroups = testTypeAltCodePRog.match(testTeamName)

	if not testTypeCodeAltGroups is None:
		test_type_team_name = testTypeCodeAltGroups.group("team_name")
		gym_type = testTypeCodeAltGroups.group("gym_type")
		test_type_code = testTypeCodeAltGroups.group("code")
	elif not testTypeCodeGroups is None:
		test_type_team_name = testTypeCodeGroups.group("team_name")
		test_type_code = testTypeCodeGroups.group("code")

	xprs_code = xprsGroups.group("code") if not xprsGroups is None else ""
	xprs_level = "A" if "A" in xprs_code else "B" if "B" in xprs_code else "C" if "C" in xprs_code else "D" if "D" in xprs_code else "E" if "E" in xprs_code else "F" if "F" in xprs_code else "-"

	return {
		"status" : "ok",
		"censor" : {
			"name" : teacherGroups.group("name") if not teacherGroups is None else unicode(soup.find("td", attrs={"id" : "m_Content_outboundcensor_teachername"}).text),
			"abbrevation" : teacherGroups.group("abbrevation") if not teacherGroups is None else ""
		},
		"test_team" : testTeamName,
		"institution" : {
			"name" : institutionGroups.group("institution") if not institutionGroups is None else soup.find("td", attrs={"id" : "m_Content_outboundcensor_institution"}).text,
			"institution_id" : institutionGroups.group("institution_id") if not institutionGroups is None else ""
		},
		"period" : {
			"start" : periodGroups.group("start") if not periodGroups is None else "",
			"end" : periodGroups.group("end") if not periodGroups is None else ""
		},
		"xprs" : {
			"xprs_test" : soup.find("td", attrs={"id" : "m_Content_outboundcensor_xprsproeve"}).text,
			"code_full" : xprs_code,
			"code" : xprs_code.replace(xprs_level, ""),
			"level" : xprs_level,
			"gym_type" : gym_type,
			"test_type_code" : test_type_code,
			"xprs_type" : xprs_type,
			"subject" : xprsGroups.group("subject_name") if not xprsGroups is None else "",
			"type" : "written" if xprs_type == "SKR" else "combined" if xprs_type == "SAM" else "oral" if xprs_type == "MDT" else xprs_type,
			"test_type_long_code" :  "Skriftlig eksamen" if xprs_type == "SKR" else "Mundtlig eksamen" if xprs_type == "MDT" else "Samlet vurdering" if xprs_type == "SAM" else xprs_type
		},
		"test_type_team_name" : test_type_team_name,
		"number_of_students" : soup.find("td", attrs={"id" : "m_Content_outboundcensor_elevtal"}).text,
		"note" : soup.find("td", attrs={"id" : "m_Content_outboundcensor_bemaerkning"}).text,
		"phases" : phases,
		"information" : information,
		"description" : description
	}