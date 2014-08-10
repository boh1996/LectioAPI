#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def field_of_studies ( config, startYear ):
	url = "https://www.lectio.dk/lectio/%s/studieretningElevTilbud.aspx?startyear=%s" % ( str(config["school_id"]), str(startYear) ).replace("{{BRANCH_ID}}", str(config["branch_id"]))
	objectList = []

	response = proxy.session.get(url)

	html = response.text

	soup = Soup(html)

	if soup.find("table", attrs={"class" : "forsideTabel"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	typeProg = re.compile(r"(?P<name>.*) \((?P<gym_type>.*)\)")
	idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/studieretningSe.aspx\?sid=(?P<field_of_study_id>.*)&prevurl=studieretningElevTilbud.aspx%3fstartyear%3d(?P<start_year>.*)")
	classProg = re.compile(r"(?P<name>.*) (?P<level>.*)$")

	rows = []

	for table in soup.findAll("table", attrs={"class" : "forsideTabel"}):
		rows = rows + table.findAll("td")

	for type in rows:
		typeNameText = type.find("div", attrs={"class" : "forsideHead"}).text.strip().encode("utf-8")
		typeGroups = typeProg.match(typeNameText)

		for field in type.findAll("a"):
			idGroups = idProg.match(field["href"])
			if not field.find("i") is None:
				classesList = field.find("i").text.replace("(", "").replace(")", "").split(", ")
			else:
				classesList = []

			classes = []

			for classText in classesList:
				classGroups = classProg.match(classText)
				classes.append({
					"name" : classGroups.group("name").strip().encode("utf-8") if not classGroups is None else "",
					"level" : classGroups.group("level").strip().encode("utf-8") if not classGroups is None else ""
				})

			objectList.append({
				"study_direction_name" : typeGroups.group("name").strip().encode("utf-8") if not typeGroups is None and "name" in typeGroups.groupdict() else typeNameText.strip().encode("utf-8"),
				"gym_type" : typeGroups.group("gym_type") if not typeGroups is None and "gym_type" in typeGroups.groupdict() else "HF" if "HF" in typeNameText else "STX" if "STX" in typeNameText else "HTX" if "HTX" in typeNameText else "HHX" if "HHX" in typeNameText else "Studenterkursus" if typeNameText == "Studenterkursus" else typeNameText.strip().encode("utf-8"),
				"start_year" : startYear,
				"gym_type_short" : "HF" if "HF" in typeNameText else "STX" if "STX" in typeNameText else "HTX" if "HTX" in typeNameText else "HHX" if "HHX" in typeNameText else "Studenterkursus" if typeNameText == "Studenterkursus" else typeNameText.strip().encode("utf-8"),
				"field_of_study_id" : idGroups.group("field_of_study_id") if not idGroups is None and "field_of_study_id" in idGroups.groupdict() else "",
				"school_id" : config["school_id"],
				"name" : field.find("b").text.strip().encode("utf-8"),
				"classes" : classes,
				"context_card_id" : "SR" + idGroups.group("field_of_study_id") if not idGroups is None and "field_of_study_id" in idGroups.groupdict() else ""
			})

	return {
		"status" : "ok",
		"list" : objectList
	}