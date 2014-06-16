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

def cleanText ( text ):
	return text.replace("\t", "").replace("\n", "").replace("\r", "").strip()

def grades ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/grades/grade_report.aspx?elevid=%s" % ( str(config["school_id"]), str(config["student_id"]) )

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

	if soup.find("table", attrs={"id" : "s_m_Content_Content_karakterView_KarakterGV"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	comments = []

	commentRows = soup.find("table", attrs={"id" : "s_m_Content_Content_remarks_grid_remarks_grid"}).findAll("tr")
	commentRows.pop(0)

	dateTime = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*)")
	dateShort = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*)")

	## Missing Test Opporunity
	for row in commentRows:
		if row.find("div") is None:
			elements = row.findAll("td")
			date = ""

			if not dateTime.match(elements[0].text) is None:
				dateTimeGroups = dateTime.match(elements[0].text)
				year = dateTimeGroups.group("year")

				if len(year) == 2:
					year = "20" + str(year)

				date = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateTimeGroups.group("day")), functions.zeroPadding(dateTimeGroups.group("month")), year, dateTimeGroups.group("hour"), dateTimeGroups.group("minute")), "%d/%m-%Y %H:%M")
			elif dateShort.match(elements[0].text):
				year = dateTimeGroups.group("year")

				if len(year) == 2:
					year = "20" + str(year)

				date = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dateTimeGroups.group("day")), functions.zeroPadding(dateTimeGroups.group("month")), year, "12", "00"), "%d/%m-%Y %H:%M")

			comments.append({
				"date" : date,
				"abbrevation" : unicode(cleanText(elements[1].text)),
				"type" : "year_grade" if unicode(cleanText(elements[2].text)) == u"Årskarakter" else "exam_grade" if unicode(cleanText(elements[2].text)) == "Examenskarakter" else unicode(cleanText(elements[2].text)),
				"student_note" : unicode(cleanText(elements[3].text))
			})

	gradeNotes = []

	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_karakterView_KarakterNoterGrid"}).findAll("tr")
	rows.pop(0)

	gradeTypeProg = re.compile(r"(?P<evaluation_type>.*) - (?P<type>.*)")
	teamProg = re.compile(r"(?P<class_name>.*) (?P<team_name>.*)")
	createdProg = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*) - (?P<teacher>.*)")
	teamElementIdProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy.aspx\?type=(?P<type_name>.*)&holdelementid=(?P<team_element_id>.*)")

	for row in rows:
		if row.find("span") is None:
			elements = row.findAll("td")

			gradeTypeGroups = gradeTypeProg.match(elements[1].text)
			evaluation_type = gradeTypeGroups.group("evaluation_type") if not gradeTypeGroups is None else ""
			grade_type = gradeTypeGroups.group("type") if not gradeTypeGroups is None else ""
			teamLementGroups = teamElementIdProg.match(elements[0].find("a")["href"])
			classGroups = teamProg.match(elements[0].find("a").text)
			createdGroups = createdProg.match(elements[3].text)
			if not createdGroups is None:
				date = datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(createdGroups.group("day")), functions.zeroPadding(createdGroups.group("month")), createdGroups.group("year"), createdGroups.group("hour"), createdGroups.group("minute")), "%d/%m-%Y %H:%M")
			else:
				date = datetime.now()

			gradeNotes.append({
				"team_full_name" : unicode(cleanText(elements[0].find("a").text)),
				"team_element_id" : teamLementGroups.group("team_element_id") if not teamLementGroups is None else "",
				"class_name" : classGroups.group("class_name") if not classGroups is None else "",
				"team_name" : classGroups.group("team_name") if not classGroups is None else "",
				"type" : "written" if grade_type == "skriftlig" else "oral",
				"evaluation_type" : "internal_test" if unicode(evaluation_type) == u"Intern prøve" else "exam_or_year_test" if unicode(evaluation_type) == u"Eksamens-/årsprøvekarakter" else "first_term" if evaluation_type == "1. standpunkt" else "second_term" if evaluation_type == "2. standpunkt" else "third_term" if evaluation_type == "3. standpunkt" else "firth_term" if evaluation_type == "4. standpunkt" else "fifth_term" if evaluation_type == "5. standpunkt" else "sixth_term",
				"grade" : elements[2].text,
				"note" : cleanText(unicode(elements[4].text)),
				"date" : date,
				"teacher_abbrevation" : unicode(createdGroups.group("teacher")) if not createdGroups is None else "",
			})

	protocolLines = []
	termProg = re.compile(r"(?P<term>.*) (?P<year>.*)")
	xprsProg = re.compile(r"(?P<code>.*) (?P<subject>.*)")
	protocolRows = soup.find("table", attrs={"id" : "s_m_Content_Content_ProtokolLinierGrid"}).findAll("tr")
	protocolRows.pop(0)

	for row in protocolRows:
		spans = row.findAll("span")
		if len(spans) > 1:
			elements = row.findAll("td")
			termGroups = termProg.match(cleanText(elements[0].text))
			term = termGroups.group("term") if not termGroups is None else ""
			xprsGroups = xprsProg.match(elements[3].find("span").text)
			teamElement = context_card.team({"school_id" : str(config["school_id"]), "context_card_id" : elements[5].find("span")["lectiocontextcard"]}, session)["team"]
			teamElement["team_element_context_card_id"] = "HE" + teamElement["team_element_id"]

			protocolLines.append({
				"grading" : "7-step" if cleanText(elements[8].text) == "7-trinsskala" else "13-step",
				"grade" : elements[7].text,
				"weight" : cleanText(elements[6].text.replace("," , ".")),
				"evaluation_type" : "oral" if cleanText(elements[4].text) == "Mundtlig" else "written" if cleanText(elements[4].text) == "Skriftlig" else "combined",
				"counts" : True if cleanText(elements[2].text) == "Ja" else False,
				"text" : "year_grade" if unicode(cleanText(elements[1].text)) == u"Årskarakter" else "exam_grade",
				"team" : {
					"name" : unicode(elements[5].find("span").text),
					"context_card_id" : elements[5].find("span")["lectiocontextcard"],
					"team_id" : elements[5].find("span")["lectiocontextcard"].replace("H", ""),
					"team_element" : teamElement
				},
				"xprs" : {
					"full_name" : unicode(elements[3].find("span").text),
					"code" : xprsGroups.group("code") if not xprsGroups is None else "",
					"subject" : xprsGroups.group("subject") if not xprsGroups is None else "",
					"xprs_subject_id" : elements[3].find("span")["lectiocontextcard"].replace("XF", ""),
					"context_card_id" : elements[3].find("span")["lectiocontextcard"]
				},
				"term" : {
					"year" : termGroups.group("year") if not termGroups is None else "",
					"term" : "summer" if term == "Sommer" else "spring" if unicode(term) == u"Forår" else "fall" if unicode(term) == u"Efterår" else "winter"
				}
			})

	gradeList = []
	termMapping = {
		u"Intern prøve" : "internal_test",
		u"Årskarakter" : "year_grade",
		u"1.standpunkt" : "first_term",
		u"2.standpunkt" : "second_term",
		u"3.standpunkt" : "third_term",
		u"4.standpunkt" : "forth_term",
		u"5.standpunkt" : "fifth_term",
		u"6.standpunkt" : "sixth_term",
		u"Eksamens-/årsprøvekarakter" : "exam_or_year_test"
	}
	gradeListRows = soup.find("table", attrs={"id" : "s_m_Content_Content_karakterView_KarakterGV"}).findAll("tr")
	headers = gradeListRows[0].findAll("th")
	headers.pop(0)
	gradeListRows.pop(0)
	teamNameProg = re.compile(r"(?P<class_name>.*) (?P<subject_name>.*), (?P<evaluation_type>.*)")

	for row in gradeListRows:
		elements = row.findAll("td")

		if elements[0].find("b") is None:
			teamGroups = teamNameProg.match(cleanText(elements[0].text))
			teamElementGroups = teamElementIdProg.match(elements[0].find("a")["href"])
			elements.pop(0)
			className = teamGroups.group("class_name") if not teamGroups is None else ""
			subject = teamGroups.group("subject_name") if not teamGroups is None else ""
			teamName = className + " " + subject

			gradeElements = []
			index = 0

			for element in elements:
				if not cleanText(element.find("div").text) == "":
					header = unicode(headers[index].text)
					term = termMapping[header] if header in termMapping else "other"
					gradeElements.append({
						"term" : term,
						"grade" : cleanText(element.find("div").text)
					})

				index = index + 1

			evaluation_type = cleanText(teamGroups.group("evaluation_type")) if not teamGroups is None else ""

			gradeList.append({
				"evaluation_type" : "oral" if evaluation_type == "mundtlig" else "written" if evaluation_type == "skriftlig" else "combined",
				"team" : {
					"class_name" : className,
					"name" : teamName,
					"subject_abbrevation" : subject,
					"team_element_id" : teamElementGroups.group("team_element_id") if not teamElementGroups is None else "",
					"school_id" : teamElementGroups.group("school_id") if not teamElementGroups is None else ""
				},
				"grades" : gradeElements
			})


	diplomaLines = []
	diplomaRows = soup.find("div", attrs={"id" : "printareaDiplomaLines"}).find("table").findAll("tr")
	diplomaRows.pop(0)
	diplomaRows.pop(0)

	subjectProg = re.compile(r"(?P<subject_name>.*) (?P<subject_level>.*)")
	subjectProgAlternative = re.compile(r"(?P<subject_name>.*) (?P<subject_level>.*) (?P<type>.*)\.")

	for row in diplomaRows:
		if row.find("span") is None:
			elements = row.findAll("td")
			if subjectProgAlternative.match(elements[0].text.strip().replace("\t", "").replace("\n", "").replace("\r", "").strip()):
				subjectGroups = subjectProgAlternative.match(elements[0].text.strip().replace("\t", "").replace("\n", "").replace("\r", "").strip())
			else:
				subjectGroups = subjectProg.match(elements[0].text.strip().replace("\t", "").replace("\n", "").replace("\r", "").strip())

			year_weight = cleanText(elements[1].text).replace(",", ".")
			year_grade = cleanText(elements[2].text)
			year_ects = cleanText(elements[3].text)
			exam_weight = cleanText(elements[4].text).replace(",", ".")
			exam_grade = cleanText(elements[5].text)
			exam_ects = cleanText(elements[6].text)

			evaluation_type = subjectGroups.group("type") if not subjectGroups is None and "type" in subjectGroups.groupdict() else None

			diplomaLines.append({
				"subject_full" : unicode(elements[0].text.replace("\t", "").replace("\n", "").replace("\r", "")),
				"subject_name" : subjectGroups.group("subject_name").replace("\t", "").replace("\n", "").replace("\r", "") if not subjectGroups is None else "",
				"subject_level" : subjectGroups.group("subject_level").replace("\t", "").replace("\n", "").replace("\r", "") if not subjectGroups is None else "",
				"year_weight" : year_weight if not year_weight.strip() == "-" and not year_weight == "??" else "waiting_for_exam" if year_weight.strip() == "??" else "unkown",
				"year_grade" : year_grade if not year_grade.strip() == "-" and not year_grade == "??" else "waiting_for_exam" if year_grade.strip() == "??" else "unkown",
				"year_ects" : year_ects if not year_ects.strip() == "-" and not year_ects == "??" else "waiting_for_exam" if year_ects.strip() == "??" else "unkown",
				"exam_weight" : exam_weight if not exam_weight.strip() == "-" and not exam_weight == "??" else "waiting_for_exam" if exam_weight.strip() == "??" else "unkown",
				"exam_grade" : exam_grade if not exam_grade.strip() == "-" and not exam_grade == "??" else "waiting_for_exam" if exam_grade.strip() == "??" else "unkown",
				"exam_ects" : exam_ects if not exam_ects.strip() == "-" and not exam_ects == "??" else "waiting_for_exam" if exam_ects.strip() == "??" else "unkown",
				"evaluation_type" : "oral" if evaluation_type == "mdt" else "written" if evaluation_type == "skr" else "combined"
			})

	avgElement = soup.find("span", attrs={"id" : "s_m_Content_Content_GradeAverageLabel"})
	for element in avgElement.findAll("span"):
		element.decompose()

	avgTextProg = re.compile(ur"Eksamensresultat ekskl\. bonus:     (?P<without_bonus>.*) Eksamensresultat inkl\. evt\. bonus: (?P<with_bonus>.*)")
	avgText = unicode(avgElement.text.strip().replace("\n", "").replace("\r", "").replace("\t", ""))
	avgGroups = avgTextProg.match(avgText)

	average = {
		"without_bonus" : avgGroups.group("without_bonus").replace(",", ".") if not avgGroups is None else "",
		"with_bonus" : avgGroups.group("with_bonus").replace(",", ".") if not avgGroups is None else ""
	}

	return {
		"status" : "ok",
		"comments" : comments,
		"grades" : gradeList,
		"grade_notes" : gradeNotes,
		"protocol_lines" : protocolLines,
		"diploma" : diplomaLines,
		"average" : average,
		"term" : {
			"value" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
			"years_string" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
		}
	}

print grades({"school_id" : 517,
	"student_id" : 4789793691,
	"username" : "boh1996",
	"password" : "jwn53yut",
	"branch_id" : "4733693427",})