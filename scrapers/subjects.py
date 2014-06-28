#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def subjects ( config ):
	teamsList = []
	url = urls.teams.replace("{{SCHOOL_ID}}", str(config["school_id"]))

	response = proxy.session.get(url)

	html = response.text

	soup = Soup(html)

	if soup.find("table", attrs={"id" : "m_Content_contenttbl"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

	idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/FindSkema.aspx\?type=(?P<type_name>.*)&fag=(?P<subject_id>.*)&(?P<the_rest>.*)")

	for initial, name in functions.grouped(rows, 2):
		groups = idProg.match(initial["href"])

		teamsList.append({
			"school_id" : config["school_id"],
			"branch_id" : config["branch_id"],
			"initial" : unicode(initial.text),
			"name" : unicode(name.text),
			"subject_id" : groups.group("subject_id") if "subject_id" in groups.groupdict() else "",
			"type" : "team" if groups.group("type_name") and "type_name" in groups.groupdict() else ""
		})

	return {
		"status" : "ok",
		"subjects" : teamsList,
		"term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
	}