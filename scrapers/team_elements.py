#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def team_elements ( config ):
	teamElementList = []
	url = urls.team_elements.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{TEAM_ID}}", str(config["team_id"]))

	response = proxy.session.get(url)

	html = response.text

	soup = Soup(html)

	if soup.find("table", attrs={"id" : "m_Content_contenttbl"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

	idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy.aspx\?type=(?P<type_name>.*)&holdelementid=(?P<team_element_id>.*)")

	for row in rows:
		groups = idProg.match(row["href"])

		teamElementList.append({
			"name" : unicode(row.text),
			"team_element_id" : groups.group("team_element_id") if "team_element_id" in groups.groupdict() else "",
			"school_id" : config["school_id"],
			"branch_id" : config["branch_id"]
		})

	return {
		"status" : "ok",
		"team_elements" : teamElementList,
		"term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
	}