#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def field_of_studies ( config, startYear ):
	url = "https://www.lectio.dk/lectio/%s/studieretningElevTilbud.aspx?startyear=%s" % ( str(config["school_id"]), str(startYear) )
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

	for type in soup.find("table", attrs={"class" : "forsideTabel"}).findAll("td"):
		typeNameText = type.find("div", attrs={"class" : "forsideHead"}).text.strip().encode("utf-8")
		typeGroups = typeProg.match(typeNameText)

		for field in type.findAll("a"):
			idGroups = idProg.match(field["href"])
			classesList = field.find("i").text.replace("(", "").replace(")", "").split(", ")

			classes = []

			for classText in classesList:
				classGroups = classProg.match(classText)
				classes.append({
					"name" : classGroups.group("name") if not classGroups is None else "",
					"level" : classGroups.group("level") if not classGroups is None else ""
				})

			objectList.append({
				"study_direction_name" : typeGroups.group("name") if "name" in typeGroups.groupdict() else "",
				"gym_type" : typeGroups.group("gym_type") if "gym_type" in typeGroups.groupdict() else "",
				"start_year" : startYear,
				"field_of_study_id" : idGroups.group("field_of_study_id") if not idGroups is None and "field_of_study_id" in idGroups.groupdict() else "",
				"school_id" : config["school_id"],
				"branch_id" : config["branch_id"],
				"name" : field.find("b").text.strip().encode("utf-8"),
				"classes" : classes
			})

	return {
		"status" : "ok",
		"list" : objectList
	}