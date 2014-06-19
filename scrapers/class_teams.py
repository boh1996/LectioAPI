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

def class_teams ( config ):

	url = "https://www.lectio.dk/lectio/%s/studieplan.aspx?klasseid=%s&displaytype=ganttkalender&ganttdimension=hold" % ( str(config["school_id"]), str(config["class_id"]) )

	# Sorting settings
	settings = {}

	cookies = {}

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

	if soup.find("div", attrs={"id" : "s_m_Content_Content_IntervalTablePnl"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	teams = []
	subjectProg = re.compile(ur"(?P<abbrevation>.*) - (?P<name>.*)")
	idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/studieplan.aspx\?holdelementid=(?P<team_element_id>.*)&displaytype=ugeteksttabel")

	for row in soup.find(attrs={"id" : "s_m_Content_Content_IntervalTablePnl"}).find("table").findAll("tr")[3:]:
		subjectGroups = subjectProg.match(row.find("a")["title"])
		idGroups = idProg.match(row.find("a")["href"])
		teams.append({
			"name" : unicode(row.find("a").text.strip()),
			"team_element_id" : idGroups.group("team_element_id") if not idGroups is None else "",
			"subject" : {
				"abbrevation" : subjectGroups.group("abbrevation") if not subjectGroups is None else "",
				"name" : subjectGroups.group("name") if not subjectGroups is None else ""
			}
		})

	return {
		"status" : "ok",
		"teams" : teams
	}