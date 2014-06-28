#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def field_of_study ( config, field_of_study_id, type = "public" ):
	url = "https://www.lectio.dk/lectio/%s/studieretningSe.aspx?sid=%s" % ( str(config["school_id"]), str(field_of_study_id) )

	objectList = []

	response = proxy.session.get(url)

	html = response.text

	soup = Soup(html)

	if soup.find("table", attrs={"id" : "studieTabel"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

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

	yearTranslations = {
		u"1. år" : "first_year",
		u"2. år" : "second_year",
		u"3. år" : "third_year",
		u"4. år" : "fourth_year",
		u"5. år" : "fifth_year",
	}

	termSemesters = {
		"1gG" : ["1. semester"],
		"1g2" : ["2. semester"],
		"2g" : ["3. semester", "4. semester"],
		"3g" : ["5. semester", "6. semester"],
		"4g" : ["7.semester", "8.semester"]
	}

	subjectTypes = {}
	group_text = ""
	electiveGroupId = "none"

	rows = soup.find("table", attrs={"id" : "studieTabel"}).findAll("tr")
	semesters = []
	yearsList = []
	semestersList = []
	semestersFound = []
	electiveGroups = []

	electiveGroupTranslations = {}

	groupId = 0
	for row in soup.find("table", attrs={"id" : "studieTabel"}).findAll("tr", attrs={"class" : "valggruppe"}):
		groupId = groupId + 1
		electiveGroups.append({
			"group_id" : groupId,
			"text" : row.find("td").text
		})
		electiveGroupTranslations[unicode(row.find("td").text)] = groupId

	if len(rows[3].findAll("td")) > 1:
		for row in rows[2].findAll("td"):
			if not row.text == "Timer":
				yearsList.append(yearTranslations[unicode(row.text)])

		for row in rows[3].findAll("td"):
			semesters.append(row.text)
	else:
		for row in rows[1].findAll("td"):
			if not row.text == "Timer":
				yearsList.append(yearTranslations[unicode(row.text)])

		for row in rows[2].findAll("td"):
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
			if unicode(group_text) in electiveGroupTranslations:
				electiveGroupId = electiveGroupTranslations[unicode(group_text)]
		elif not subjectType is None:
			if not "class" in row.findAll("td")[0].attrs or not "bundTekst" in row.findAll("td")[0].attrs["class"]:
				name = ""
				level = ""
				terms = []
				hours = 0
				typeName = "standard_subject"
				index = 0

				for element in row.findAll("td"):
					if "class" in element.attrs:
						if "class" in element.attrs and "timer" in element.attrs["class"]:
							hours = element.text
						else:
							if not element.find("span") is None:
								'''if "programsubject" in element["class"] and not "1_term" in terms:
									terms.append("1_term")'''
								if type == "student" and "notchosensubject" in element["class"]:
									typeName = "not_chosen_subject"
								if len(semesters) > index and unicode(semesters[index]) in semester_translations:
									terms.append(semester_translations[unicode(semesters[index])])
									if not unicode(semesters[index]) in semestersFound:
										semestersList.append(semester_translations[unicode(semesters[index])])
										semestersFound.append(unicode(semesters[index]))
								else:
									termName = " ".join(element["class"]).replace("programsubject", "").replace("notchosensubject", "").strip()
									if termName in termSemesters:
										for item in termSemesters[termName]:
											terms.append(semester_translations[unicode(item)])

											if not unicode(item) in semestersFound:
												semestersList.append(semester_translations[unicode(item)])
												semestersFound.append(unicode(item))

								if name == "" and not element.find("span") is None:
									nameGroups = nameProg.match(element.find("span").text)
									name = nameGroups.group("name") if not nameGroups is None else element.find("span").text
									level = nameGroups.group("level") if not nameGroups is None else "C"
					else:
						subjectTypes[subjectType]["presentation"] = element.encode("utf-8")

					index = index + 1

				objectList.append({
					"subject_type" : subjectType,
					"name" : name.encode("utf8"),
					"level" : level.encode("utf8"),
					"terms" : terms,
					"hours" : hours,
					"type" : typeName.encode("utf8"),
					"group_text" : group_text.encode("utf8"),
					"subject_group_id" : electiveGroupId
				})

	return {
		"status" : "ok",
		"semesters" : semestersList,
		"years" : yearsList,
		"subjects" : objectList,
		"subject_types" : subjectTypes,
		"elective_groups" : electiveGroups,
		"presentation" : soup.find("td", attrs={"id" : "m_Content_StudieretningPresentationCtrl1_footertd"}).text.encode("utf-8") if len(soup.find("td", attrs={"id" : "m_Content_StudieretningPresentationCtrl1_footertd"}).text) > 1 else soup.find(attrs={"id" : "m_Content_StudieretningPresentationCtrl1_footerwebsitelinkTR"}).text
	}