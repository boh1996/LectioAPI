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

def electives ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/studieretningValgfag.aspx?elevid=%s" % ( str(config["school_id"]), str(config["student_id"]) )

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

	if soup.find("div", attrs={"id" : "s_m_Content_Content_ValgfagstilmeldingIsland_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	tables = soup.find("div", attrs={"id" : "s_m_Content_Content_ValgfagstilmeldingIsland_pa"}).findAll("table")

	subjectType = None
	nameProg = re.compile(r"(?P<name>.*) (?P<level>.)$")

	semester_translations = {
		u"1. semester" : {
			"year" : 1,
			"term" : 1,
			"text" : "first_year_first_term"
		},
		u"2. semester" : {
			"year" : 1,
			"term" : 2,
			"text" : "first_year_second_term"
		},
		u"3. semester" : {
			"year" : 2,
			"term" : 1,
			"text" : "second_year_first_term"
		},
		u"4. semester" : {
			"year" : 2,
			"term" : 2,
			"text" : "second_year_second_term"
		},
		u"5. semester" : {
			"year" : 3,
			"term" : 1,
			"text" : "third_year_first_term"
		},
		u"6. semester" : {
			"year" : 3,
			"term" : 2,
			"text" : "third_year_second_term"
		},
		u"7.semester" : {
			"year" : 4,
			"term" : 1,
			"text" : "fourth_year_first_term"
		},
		u"8.semester" : {
			"year" : 4,
			"term" : 2,
			"text" : "fourth_year_second_term"
		},
		u"9.semester" : {
			"year" : 5,
			"term" : 1,
			"text" : "fifth_year_first_term"
		},
		u"10.semester" : {
			"year" : 5,
			"term" : 2,
			"text" : "fifth_year_second_term"
		},
	}

	termSemesters = {
		"1gG" : ["1. semester"],
		"1g2" : ["2. semester"],
		"2g" : ["3. semester", "4. semester"],
		"3g" : ["5. semester", "6. semester"],
		"4g" : ["7.semester", "8.semester"]
	}

	subjectTypes = {}
	group_text = "standard"
	options = []

	rows = soup.find("table", attrs={"id" : "studieTabel"}).findAll("tr")
	semesters = []

	if len(rows[2].findAll("td")) > 1:
		for row in rows[2].findAll("td"):
			if not unicode(row.text) == u"Obligatoriske fag":
				semesters.append(row.text)
	else:
		for row in rows[3].findAll("td"):
			if not unicode(row.text) == u"Obligatoriske fag":
				semesters.append(row.text)

	for row in soup.find("table", attrs={"id" : "studieTabel"}).findAll("tr"):
		if "class" in row.attrs and "fagtype" in row.attrs["class"]:
			subjectType = "mandatory" if row.find("td").text == "Obligatoriske fag" else "specialized" if row.find("td").text == "Studieretningsfag" else "electives"
			if not subjectType in subjectTypes:
				subjectTypes[subjectType] = {
					"name" : subjectType,
					"presentation" : ""
				}
		elif "class" in row.attrs and "valggruppe" in row.attrs["class"]:
			group_text = row.findAll("td")[0].text
		elif not subjectType is None:
			if not "class" in row.findAll("td")[0].attrs or not "bundTekst" in row.findAll("td")[0].attrs["class"]:
				name = ""
				level = ""
				terms = []
				hours = 0
				typeName = "standard_subject"
				index = 0
				chosen = False

				for element in row.findAll("td"):
					if "class" in element.attrs:
						if "class" in element.attrs and "timer" in element.attrs["class"]:
							hours = element.text
						else:
							if not element.find("span") is None:
								if "chosensubject" in element["class"]:
									chosen = True
								'''if "programsubject" in element["class"] and not "1_term" in terms:
									terms.append("1_term")'''
								if type == "student" and "notchosensubject" in element["class"]:
									typeName = "not_chosen_subject"
								if len(semesters) > 0 and index in semesters and unicode(semesters[index]) in semester_translations:
									terms.append(semester_translations[unicode(semesters[index])])
								else:
									termName = " ".join(element["class"]).replace("programsubject", "").replace("notchosensubject", "").strip()
									if termName in termSemesters:
										for item in termSemesters[termName]:
											terms.append(semester_translations[unicode(item)])

								if name == "" and not element.find("span") is None:
									nameGroups = nameProg.match(element.find("span").text)
									name = nameGroups.group("name") if not nameGroups is None else element.find("span").text
									level = nameGroups.group("level") if not nameGroups is None else "C"
					else:
						subjectTypes[subjectType]["presentation"] = element.encode("utf-8")

					index = index + 1

				options.append({
					"subject_type" : subjectType,
					"name" : name.encode("utf8"),
					"level" : level.encode("utf8"),
					"terms" : terms,
					"hours" : hours,
					"type" : typeName.encode("utf8"),
					"group_text" : group_text.encode("utf8"),
					"chosen" : chosen
				})

	informationElements = tables[0].findAll("td")
	fieldOfStudyProg = re.compile(r"(?P<term>[.^\S]*) (?P<name>.*)$")
	fieldOfStudyGroups = fieldOfStudyProg.match(informationElements[2].find("span").text)
	information = {
		"student_type" : unicode(informationElements[0].text),
		"start_term" : informationElements[1].text,
		"field_of_study" : {
			"term" : fieldOfStudyGroups.group("term") if not fieldOfStudyGroups is None else "",
			"name" : fieldOfStudyGroups.group("name") if not fieldOfStudyGroups is None else "",
			"context_card_id" : informationElements[2].find("span")["lectiocontextcard"],
			"field_of_study_id" : informationElements[2].find("span")["lectiocontextcard"].replace("SR", ""),
			"presentation" : unicode(soup.find(attrs={"class" : "bundTekst"}).text),
			"attention" : unicode(informationElements[2].find(attrs={"class" : "attention"}).text) if not informationElements[2].find(attrs={"class" : "attention"}) is None else ""
		},
		"deadline" : {
			"text" : "over" if unicode(informationElements[3].text) == u"Der er nu lukket for redigering af valgfalgsønsker" else unicode(informationElements[3].text)
		},
		"description" : unicode(informationElements[4].text.strip("\n"))
	}
	choices = []

	seasons = {
		u"Efterår" : "fall",
		u"Sommer" : "summer",
		u"Forår" : "spring",
		u"Vinter" : "winter"
	}

	if not soup.find(attrs={"id" : "s_m_Content_Content_valgfagGrid"}) is None and soup.find(attrs={"id" : "s_m_Content_Content_valgfagGrid"}).find(attrs={"class" : "noRecord"}) is None:
		rows = soup.find(attrs={"id" : "s_m_Content_Content_valgfagGrid"}).findAll("tr")[1:]

		choiceProg = re.compile(ur"(?P<term>.*) - (?P<season>.*) \((?P<semester>.*)\)")
		subjectProg = re.compile(r"(?P<code>[.^\S]) (?P<name>.*)")

		for row in rows:
			elements = row.findAll("td")
			choiceGroups = choiceProg.match(elements[0].text.replace("\r\n", "").replace("\t", "").strip("\n").strip())
			firstChoiceGroups = None
			secondChoiceGroups = None
			if "lectiocontextcard" in elements[2].find("span").attrs:
				firstChoiceGroups = subjectProg.match(elements[2].text)

			if "lectiocontextcard" in elements[3].find("span").attrs:
				secondChoiceGroups = subjectProg.match(elements[3].text)

			choices.append({
				"comment" : unicode(elements[4].text.replace("\r\n", "").replace("\t", "").strip("\n")),
				"description" : unicode(elements[1].text).replace('"', ''),
				"start_term" : choiceGroups.group("term") if not choiceGroups is None else "",
				"start_season" : seasons[unicode(choiceGroups.group("season"))] if not choiceGroups is None else "",
				"start_semester" : choiceGroups.group("semester").replace(".", "") if not choiceGroups is None else "",
				"year_text" : elements[0].text,
				"first" : {
					"context_card_id" : elements[2].find("span")["lectiocontextcard"] if "lectiocontextcard" in elements[2].find("span").attrs else "",
					"subject_id" : elements[2].find("span")["lectiocontextcard"].replace("XF", "") if "lectiocontextcard" in elements[2].find("span").attrs else "",
					"active" : True if "lectiocontextcard" in elements[2].find("span").attrs else False,
					"name" : firstChoiceGroups.group("name") if not firstChoiceGroups is None else "",
					"code" : firstChoiceGroups.group("code") if not firstChoiceGroups is None else ""
				},
				"second" : {
					"context_card_id" : elements[3].find("span")["lectiocontextcard"] if "lectiocontextcard" in elements[3].find("span").attrs else "",
					"subject_id" : elements[3].find("span")["lectiocontextcard"].replace("XF", "") if "lectiocontextcard" in elements[3].find("span").attrs else "",
					"active" : True if "lectiocontextcard" in elements[3].find("span").attrs else False,
					"name" : firstChoiceGroups.group("name") if not firstChoiceGroups is None else "",
					"code" : firstChoiceGroups.group("code") if not firstChoiceGroups is None else ""
				}
			})

	return {
		"status" : "ok",
		"information" : information,
		"choices" : choices,
		"options" : options
	}