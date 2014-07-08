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
import context_card

def student_surveys ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/spoergeskema_rapport.aspx?type=mine&elevid=%s" % ( str(config["school_id"]), str(config["student_id"]) )

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

	if soup.find("div", attrs={"id" : "s_m_Content_Content_answer_island_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}
	surveys = []
	ids = []

	openForAnsweringProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/spoergeskema_besvar.aspx\?id=(?P<survey_id>.*)&prevurl=(?P<prev_url>.*)")
	ownProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/spoergeskema_rediger.aspx\?id=(?P<survey_id>.*)&prevurl=(?P<prev_url>.*)")
	openForReportingProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/spoergeskema\/spoergeskemarapportering.aspx\?id=(?P<survey_id>.*)&prevurl=(?P<prev_url>.*)")
	dateTimeProg = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*)")

	if soup.find(attrs={"id" : "s_m_Content_Content_answer_island_pa"}).find("table").find(attrs={"class" : "noRecord"}) is None:
		for row in soup.find(attrs={"id" : "s_m_Content_Content_answer_island_pa"}).findAll("tr")[1:]:
			elements = row.findAll("td")
			if not elements[3].find("span") is None:
				dateGroups = dateTimeProg.match(elements[3].find("span").text.strip())
			else:
				dateGroups = dateTimeProg.match(elements[3].text)
			date = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""
			idGroups = openForAnsweringProg.match(elements[0].find("a")["href"])
			id = idGroups.group("survey_id") if not idGroups is None else ""
			ids.append(id)
			surveys.append({
				"types" : ["open_for_answering"],
				"survey_id" : id,
				"anonymous" : True if elements[2].text == "Ja" else False,
				"answer_date" : date,
				"title" : elements[0].text.strip().replace("\r", "").replace("\n", "").replace("\t", "").encode("utf8")
			})

	if soup.find(attrs={"id" : "s_m_Content_Content_report_island_pa"}).find(attrs={"class" : "noRecord"}) is None:
		for row in soup.find(attrs={"id" : "s_m_Content_Content_report_island_pa"}).findAll("tr")[1:]:
			elements = row.findAll("td")
			if not elements[2].find("span") is None:
				dateGroups = dateTimeProg.match(elements[2].find("span").text.strip())
			else:
				dateGroups = dateTimeProg.match(elements[2].text)
			answerDate = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""
			dateGroups = dateTimeProg.match(elements[3].text)
			reportDate = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""
			dateGroups = dateTimeProg.match(elements[4].text)
			endDate = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""
			idGroups = openForReportingProg.match(elements[0].find("a")["href"])
			id = idGroups.group("survey_id") if not idGroups is None else ""
			ids.append(id)

			if id in ids:
				for x in surveys:
					if x["survey_id"] == id:
						x["answer_date"] = answerDate
						x["report_date"] = reportDate
						x["end_date"] = endDate
						x["types"].append("open_for_reporting")
			else:
				surveys.append({
					"types" : "open_for_reporting",
					"survey_id" : id,
					"answer_date" : answerDate,
					"report_date" : reportDate,
					"end_date" : endDate,
					"title" : elements[0].text.strip().replace("\r", "").replace("\n", "").replace("\t", "").encode("utf8")
				})

	if soup.find(attrs={"id" : "s_m_Content_Content_own_island_pa"}).find(attrs={"class" : "noRecord"}) is None:
		for row in soup.find(attrs={"id" : "s_m_Content_Content_own_island_pa"}).findAll("tr")[1:]:
			elements = row.findAll("td")
			if not elements[1].find("span") is None:
				dateGroups = dateTimeProg.match(elements[1].find("span").text.strip())
			else:
				dateGroups = dateTimeProg.match(elements[1].text)
			answerDate = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""
			dateGroups = dateTimeProg.match(elements[2].text)
			reportDate = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""
			dateGroups = dateTimeProg.match(elements[3].text)
			endDate = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""
			idGroups = ownProg.match(elements[0].find("a")["href"])
			id = idGroups.group("survey_id") if not idGroups is None else ""

			if id in ids:
				for x in surveys:
					if x["survey_id"] == id:
						x["owner_id"] = str(config["student_id"])
						x["answer_date"] = answerDate
						x["report_date"] = reportDate
						x["end_date"] = endDate

			else:
				ids.append(id)
				surveys.append({
					"types" : ["closed"],
					"survey_id" : id,
					"answer_date" : answerDate,
					"report_date" : reportDate,
					"end_date" : endDate,
					"title" : elements[0].text.strip().replace("\r", "").replace("\n", "").replace("\t", "").encode("utf8")
				})

		return {
			"status" : "ok",
			"surveys" : surveys
		}

def survey_answer_page ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/spoergeskema_besvar.aspx?id=%s" % ( str(config["school_id"]), str(config["survey_id"]) )

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

	if soup.find("table", attrs={"id" : "m_Content_InfoTable"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	elements = soup.find("table", attrs={"id" : "m_Content_InfoTable"}).findAll("td")

	owner = context_card.user({
		"context_card_id" : elements[1].find("span")["lectiocontextcard"],
		"school_id" : str(config["school_id"])
	}, session)["user"]

	ownerUser = {
		"context_cards" : [elements[1].find("span")["lectiocontextcard"], owner["context_card_id"]],
		"picture_id" : owner["picture_id"],
		"name" : owner["name"],
		"type" : owner["type"]
	}

	if owner["type"] == "student":
		ownerUser["student_id"] = owner["student_id"]
	else:
		ownerUser["teacher_id"] = owner["teacher_id"]

	information = {
		"title" : elements[0].text.encode("utf8"),
		"owner" : ownerUser,
		"anonymous" : True if elements[2].text == "Ja" else False,
		"teachers" : elements[3].text.split(", "),
		"teams" : elements[4].text.split(", ")
	}

	sections = []

	section_number = None
	section_title = None
	section_elements = []
	section_description = None

	titleProg = re.compile(r"(?P<number>[\d]*) (?P<title>.*)")
	subTitleProg = re.compile(r"(?P<number>[\d\.\d\S]*) (?P<title>.*)")

	for row in soup.find(attrs={"id" : "m_Content_questionIsland2_pa"}).findAll("table"):
		if row.find("h3") is None:
			if not row.find(attrs={"type" : "RADIO"}) is None:
				type = "radio"
			elif not row.find(attrs={"type" : "CHECKBOX"}) is None:
				type = "checkbox"
			else:
				type = "text"

			lines = row.find("h4").text.replace("\t", "").replace("\r", "").strip().split("\n")

			titleGroups = subTitleProg.match(str(lines[0]) + " " + str(lines[1]))

			options = []

			section_id = None

			if type == "text":
				section_id = row.find("textarea")["name"].replace("answer_", "")
				options.append({
					"type" : "text",
					"name" : row.find("textarea")["name"]
				})
			else:
				for element in row.findAll("div"):
					section_id = element.find("input")["name"].replace("answer_", "")
					options.append({
						"title" : element.find("label").text.encode("utf8"),
						"value" : element.find("input")["value"],
						"name" : element.find("input")["name"],
						"type" : type
					})

			section_elements.append({
				"type" : type,
				"title" : titleGroups.group("title") if not titleGroups is None else "",
				"description" : row.find(attrs={"class" : "discreteCell"}).text.replace("\r", "").replace("\n", "").replace("\t", "").strip(),
				"number" : titleGroups.group("number") if not titleGroups is None else "",
				"options" : options,
				"section_id" : section_id
			})
		else:
			if not section_number is None:
				sections.append({
					"number" : section_number,
					"title" : section_title,
					"elements" : section_elements,
					"description" : section_description
				})

				section_number = None
				section_title = None
				section_elements = []
				section_description = None

			lines = row.find("h3").text.replace("\t", "").replace("\r", "").strip().split("\n")

			titleGroups = titleProg.match(str(lines[0]) + " " + str(lines[1]))

			section_number = titleGroups.group("number") if not titleGroups is None else None
			section_title = titleGroups.group("title") if not titleGroups is None else None
			section_description = row.find(attrs={"class" : "discreteCell"}).text.replace("\r\n", "").replace("\t", "").strip()

	if section_number == None:
		section_number = 1
		section_title = ""
		section_description = ""

	sections.append({
		"number" : section_number,
		"title" : section_title,
		"elements" : section_elements,
		"description" : section_description
	})

	return {
		"status" : "ok",
		"information" : information,
		"sections" : sections
	}

def survey_report ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/spoergeskema/spoergeskemarapportering.aspx?id=%s" % ( str(config["school_id"]), str(config["survey_id"]) )

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

	if soup.find("div", attrs={"id" : "m_Content_sdasd_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	dateTimeProg = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*)")

	informationTables = soup.find("div", attrs={"id" : "m_Content_sdasd_pa"}).findAll("table")
	infoElements = informationTables[0].findAll("td")

	dateGroups = dateTimeProg.match(infoElements[2].text)
	answerDate = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("hour"), dateGroups.group("minute")), "%d/%m-%Y %H:%M") if not dateGroups is None else ""

	owner = context_card.user({
		"context_card_id" : infoElements[1].find("span")["lectiocontextcard"],
		"school_id" : str(config["school_id"])
	}, session)["user"]

	ownerUser = {
		"context_cards" : [infoElements[1].find("span")["lectiocontextcard"], owner["context_card_id"]],
		"picture_id" : owner["picture_id"],
		"name" : owner["name"],
		"type" : owner["type"]
	}

	if owner["type"] == "student":
		ownerUser["student_id"] = owner["student_id"]
	else:
		ownerUser["teacher_id"] = owner["teacher_id"]

	information = {
		"title" : infoElements[0].text.encode("utf8"),
		"answer_date" : answerDate,
		"owner" : ownerUser
	}

	statElements = informationTables[1].findAll("td")

	stats = {
		"teachers" : {
			"registred" : statElements[1].text,
			"submitted" : statElements[2].text,
			"submitted_with_unsubscribed" : statElements[3].text,
			"not_submitted" : statElements[4].text
		},
		"students" : {
			"registred" : statElements[5].text,
			"submitted" : statElements[6].text,
			"submitted_with_unsubscribed" : statElements[7].text,
			"not_submitted" : statElements[8].text
		},
		"total" : {
			"registred" : statElements[9].text,
			"submitted" : statElements[10].text,
			"submitted_with_unsubscribed" : statElements[11].text,
			"not_submitted" : statElements[12].text
		}
	}

	sections = []

	section_number = None
	section_title = None
	section_elements = []
	section_description = None

	current_question_title = None
	current_question_number = None
	current_question_description = None

	titleProg = re.compile(r"(?P<number>[\d\.\d\S]*) (?P<title>.*)")

	type = "text"
	answerStats = []
	unanswered = 0
	unansweredPercent = 0

	for row in soup.find(attrs={"id" : "m_Content_ctl00_pa"}).find("table").findAll("tr", recursive=False):
		elements = row.findAll("td")

		text = elements[0].text.strip().replace("\r", "").replace("\t", "")

		if len(text) > 0:
			if not elements[0].find("h3") is None:
				titleGroups = titleProg.match(elements[0].find("h3").text)

				if not "." in titleGroups.group("number"):
					if not section_number is None:
						sections.append({
							"number" : section_number,
							"title" : section_title,
							"elements" : section_elements,
							"description" : section_description
						})

						section_number = None
						section_title = None
						section_elements = []
						section_description = None

					section_number = titleGroups.group("number") if not titleGroups is None else None
					section_title = titleGroups.group("title") if not titleGroups is None else None
					elements[0].find("h3").decompose()
					section_description = elements[0].text.replace("\r\n", "").replace("\t", "").strip().strip("\n")
				else:
					current_question_number = titleGroups.group("number") if not titleGroups is None else None
					current_question_title = titleGroups.group("title") if not titleGroups is None else None
					elements[0].find("h3").decompose()
					current_question_description = elements[0].text.replace("\r\n", "").replace("\t", "").strip().strip("\n")
			else:
				tables = row.findAll("table")
				answers = []

				if tables[0].find("img") is None:
					for x in tables[0].findAll("tr"):
						xElements = x.findAll("td")

						if type == "checkbox":
							options = xElements[3].text.split(", ")
						else:
							options = [xElements[3].text]

						if xElements[2].text == "anonym":
							answers.append({
								"anonymous" : True,
								"respondent_id" : xElements[0].text,
								"options" : options
							})
						else:
							answers.append({
								"anonymous" : False,
								"options" : options,
								"user_context_card_id" : xElements[0].find("span")["lectiocontextcard"],
								"user_text_id" : xElements[1].text,
								"user_team_text" : xElements[2].text
							})


					section_elements.append({
						"number" : current_question_number.encode("utf8"),
						"title" : current_question_title.encode("utf8"),
						"description" : current_question_description.encode("utf8"),
						"type" : type,
						"answers" : answers,
						"answer_stats" : answerStats,
						"unanswered" : str(unanswered),
						"unanswered_percent" : str(unansweredPercent)
					})

					type = "text"
					answerStats = []
					unanswered = 0
					unansweredPercent = 0
				else:
					for x in tables[0].findAll("tr"):
						xElements = x.findAll("td")
						if x.find("th").text == "Ubesvaret":
							type = "radio"
							unanswered = xElements[1].text
							unansweredPercent = xElements[2].text.replace(" %", "")
						else:
							type = "checkbox"
							answerStats.append({
								"text" : x.find("th").text.encode("utf8"),
								"number" : xElements[1].text,
								"percent" : xElements[2].text.replace(" %", "").replace(",", ".")
							})

	if section_number == None:
		section_number = 1
		section_title = ""
		section_description = ""

	sections.append({
		"number" : section_number,
		"title" : section_title,
		"elements" : section_elements,
		"description" : section_description
	})

	return {
		"status" : "ok",
		"information" : information,
		"stats" : stats,
		"sections" : sections
	}

def templates ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/spoergeskema/skabeloner.aspx?elevid=%s" % ( str(config["school_id"]), str(config["student_id"]) )

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

	if soup.find("div", attrs={"id" : "s_m_Content_Content_createQueryIsland_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	templates = []

	ownSchoolProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/spoergeskema_besvar.aspx\?mode=display&id=(?P<survey_id>.*)&prevurl=(?P<prev_url>.*)")

	if not soup.find("div", attrs={"id" : "s_m_Content_Content_createQueryIsland_pa"}).find(attrs={"class" : "noRecord"}):
		for row in soup.find("div", attrs={"id" : "s_m_Content_Content_createQueryIsland_pa"}).findAll("tr")[1:]:
			idGroups = ownSchoolProg.match(row.find("a")["href"])
			templates.append({
				"school_id" : str(config["school_id"]),
				"branch_id" : str(config["school_id"]),
				"title" : row.find("a").text.encode("utf8"),
				"survey_id" : idGroups.group("survey_id") if not idGroups is None else "",
				"template" : True
			})

	if not soup.find("div", attrs={"id" : "s_m_Content_Content_LectioDetailIsland1_pa"}).find(attrs={"class" : "noRecord"}):
		for row in soup.find("div", attrs={"id" : "s_m_Content_Content_LectioDetailIsland1_pa"}).findAll("tr")[1:]:
			idGroups = ownSchoolProg.match(row.find("a")["href"])
			elements = row.findAll("td")
			templates.append({
				"title" : row.find("a").text.encode("utf8"),
				"survey_id" : idGroups.group("survey_id") if not idGroups is None else "",
				"school_name" : elements[1].text.encode("utf8"),
				"owner_name" : elements[2].text.encode("utf8"),
				"template" : True
		})

	return {
		"status" : "ok",
		"templates" : templates
	}