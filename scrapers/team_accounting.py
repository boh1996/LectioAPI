#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def team_accounting ( config ):
	url = "https://www.lectio.dk/lectio/%s/subnav/modulregnskab.aspx?holdelementid=%s" % ( str(config["school_id"]), str(config["team_element_id"]) )

	response = proxy.session.get(url)

	html = response.text

	soup = Soup(html)

	if soup.find("table", attrs={"id" : "s_m_Content_Content_afholdtelektionertbl"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_afholdtelektionertbl"}).findAll("tr")

	rows.pop(0)
	rows.pop(0)

	totalColumns = rows[0].findAll("td")
	totalColumns.pop(0)

	total = {
		"total": {
			"education" : {
				"held" : totalColumns[0].text if not totalColumns[0].text == "" else 0,
				"planned" : totalColumns[1].text if not totalColumns[1].text == "" else 0
			},
			"other_activity" : {
				"held" : totalColumns[2].text if not totalColumns[2].text == "" else 0,
				"planned" : totalColumns[3].text if not totalColumns[3].text == "" else 0
			},
			"total" : totalColumns[4].text if not totalColumns[4].text == "" else 0,
			"standard" : totalColumns[5].text if not totalColumns[5].text == "" else 0,
			"deviation" : totalColumns[6].text.replace(",", ".") if not totalColumns[6].text == "" else 0
		},
		"without_teacher" : {}
	}

	rows.pop(0)

	teachers = []

	for row in rows:
		columns = row.findAll("td")
		if unicode(columns[0].text) == u"Uden lærerkreditering":
			columns.pop(0)
			total["without_teacher"] = {
				"education" : {
					"held" : columns[0].text if not columns[0].text == "" else 0,
					"planned" : columns[1].text  if not columns[1].text == "" else 0
				},
				"other_activity" : {
					"held" : columns[2].text if not columns[2].text == "" else 0,
					"planned" : columns[3].text if not columns[3].text == "" else 0
				},
				"total" : columns[4].text  if not columns[4].text == "" else 0,
				"standard" : columns[5].text  if not columns[5].text == "" else 0,
				"deviation" : columns[6].text.replace(",", ".")  if not columns[6].text == "" else 0
			}
		else:
			name = unicode(columns[0].text)
			nameProg = re.compile(r"(?P<name>.*) \((?P<abbrevation>.*)\)")
			nameGroups = nameProg.match(name)
			columns.pop(0)
			teachers.append({
				"name" : nameGroups.group("name") if not nameGroups is None else name,
				"abbrevation" : nameGroups.group("abbrevation") if not nameGroups is None else "",
				"education" : {
					"held" : columns[0].text if not columns[0].text == "" else 0,
					"planned" : columns[1].text  if not columns[1].text == "" else 0
				},
				"other_activity" : {
					"held" : columns[2].text if not columns[2].text == "" else 0,
					"planned" : columns[3].text if not columns[3].text == "" else 0
				},
				"total" : columns[4].text  if not columns[4].text == "" else 0,
				"standard" : columns[5].text  if not columns[5].text == "" else 0,
				"deviation" : columns[6].text.replace(",", ".")  if not columns[6].text == "" else 0
			})

	return {
		"status" : "ok",
		"total"  : total,
		"teachers" : teachers
	}