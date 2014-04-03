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
	nameProg = re.compile(r"(?P<name>.*) (?P<level>.*)$")
	termTranslations = {
		"1gG" : "1_term_basic",
		"1g2" : "1_term_second",
		"2g" : "2_term",
		"3g" : "3_term"
	}
	subjectTypes = {}
	group_text = "standard"

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

				for element in row.findAll("td"):
					if "class" in element.attrs:
						if "class" in element.attrs and "timer" in element.attrs["class"]:
							hours = element.text
						else:
							if not element.find("span") is None:
								if "programsubject" in element["class"] and not "1_term" in terms:
									terms.append("1_term")
								if type == "student" and "notchosensubject" in element["class"]:
									typeName = "not_chosen_subject"
								termName = " ".join(element["class"]).replace("programsubject", "").replace("notchosensubject", "").strip()
								terms.append(termTranslations[termName])
								if name == "" and not element.find("span") is None:
									nameGroups = nameProg.match(element.find("span").text)
									name = nameGroups.group("name") if not nameGroups is None else ""
									level = nameGroups.group("level") if not nameGroups is None else ""
					else:
						subjectTypes[subjectType]["presentation"] = element.encode("utf-8")

				objectList.append({
					"subject_type" : subjectType,
					"name" : name.encode("utf8"),
					"level" : level.encode("utf8"),
					"terms" : terms,
					"hours" : hours,
					"type" : typeName.encode("utf8"),
					"group_text" : group_text.encode("utf8")
				})

	return {
		"status" : "ok",
		"objectList" : objectList,
		"subject_types" : subjectTypes,
		"presentation" : soup.find("td", attrs={"id" : "m_Content_StudieretningPresentationCtrl1_footertd"}).text.encode("utf-8")
	}

print field_of_study({"school_id" : 517}, 7311376919)