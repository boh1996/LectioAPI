#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def groups ( config ):
	groupsList = []
	url = urls.groups_list.replace("{{SCHOOL_ID}}", str(config["school_id"]))

	response = proxy.session.get(url)

	html = response.text

	soup = Soup(html)

	if soup.find("table", attrs={"id" : "m_Content_contenttbl"}) is None or soup.find("table", attrs={"id" : "m_Content_contenttbl2"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	buildInGroupRows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

	idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy.aspx\?type=(?P<type_name>.*)&holdelementid=(?P<group_id>.*)")

	for row in buildInGroupRows:
		idGroups = idProg.match(row["href"])

		groupsList.append({
			"school_id" : config["school_id"],
			"branch_id" : config["branch_id"],
			"name" : unicode(row.text),
			"group_id" : idGroups.group("group_id") if "group_id" in idGroups.groupdict() else "",
			"type" : idGroups.group("type_name") if "type_name" in idGroups.groupdict() else "",
			"group_type" : "build_in"
		})

	ownGroupRows = soup.find("table", attrs={"id" : "m_Content_contenttbl2"}).findAll("a")

	for row in ownGroupRows:
		idGroups = idProg.match(row["href"])

		groupsList.append({
			"school_id" : config["school_id"],
			"branch_id" : config["branch_id"],
			"name" : unicode(row.text),
			"group_id" : idGroups.group("group_id") if "group_id" in idGroups.groupdict() else "",
			"type" : idGroups.group("type_name") if "type_name" in idGroups.groupdict() else "",
			"group_type" : "own_group"
		})

	return {
		"status" : "ok",
		"groups" : groupsList,
		"term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
	}