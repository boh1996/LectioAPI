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

def materials ( config ):
	url = "https://www.lectio.dk/lectio/%s/MaterialOverview.aspx?holdelement_id=%s" % ( str(config["school_id"]), str(config["team_element_id"]) )

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

	if soup.find("table", attrs={"id" : "m_Content_MaterialsStudents"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "m_Content_MaterialsStudents"}).findAll("tr")
	materialsList = []

	if len(rows) > 1:
		rows.pop(0)
		titleProg = re.compile(ur"(?P<authors>.*): (?P<title>.*), (?P<publisher>.*)")

		for row in rows:
			elements = row.findAll("td")
			title = unicode(elements[0].text.replace("\n", ""))
			titleGroups = titleProg.match(title)
			materialsList.append({
				"title_text" : title,
				"title" : titleGroups.group("title") if not titleGroups is None else title,
				"publisher" : titleGroups.group("publisher") if not titleGroups is None else "",
				"authors" : titleGroups.group("authors").split(", ") if not titleGroups is None else "",
				"type" : "book" if unicode(elements[1].text.replace("\n", "")) == u"Bog" else unicode(elements[1].text.replace("\n", "")),
				"book_storage" : True if elements[2].text.replace("\n", "") == "Ja" else False,
				"comment" : unicode(elements[3].text.strip("\n").replace("\n", "")),
				"ebook" : elements[4].text.strip("\n").replace("\n", "")
			})

	return {
		"status" : "ok",
		"materials" : materialsList
	}