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

def skills ( config ):
	url = "https://www.lectio.dk/lectio/%s/studieplan.aspx?holdelementid=%s&displaytype=holdogkompetence" % ( str(config["school_id"]), str(config["team_element_id"]) )

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

	if soup.find("table", attrs={"id" : "s_m_Content_Content_CompetanceTbl"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_CompetanceTbl"}).findAll("tr")
	rows.pop(0)

	lastLevel = None
	header =  None
	headerElemenets = []
	skilsList = []

	for row in rows:
		elements = row.findAll("td")
		level = elements[len(elements)-2]["colspan"]
		if lastLevel is None:
			header = unicode(elements[len(elements)-2].text)
		elif level > lastLevel:
			skilsList.append({
				"header" : header,
				"elements" : headerElemenets
			})
			headerElemenets = []

			header = unicode(elements[len(elements)-2].text)
		else:
			headerElemenets.append(elements[len(elements)-2].text)
		lastLevel = level

	skilsList.append({
		"header" : header,
		"elements" : headerElemenets
	})

	return {
		"status" : "ok",
		"skils" : skilsList.
		"term" : {
			"value" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
			"years_string" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
		}
	}