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

def school_info ( config ):
	url = "https://www.lectio.dk/lectio/%s/default.aspx" % ( str(config["school_id"]) )

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
	idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaUgeaendringer.aspx\?lecafdeling=(?P<branch_id>.*)")

	if soup.find("ul", attrs={"class" : "linklist"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	elements = soup.find("ul", attrs={"class" : "linklist"}).findAll("a")
	idGroups = idProg.match(elements[1]["href"])
	terms = []

	for row in soup.find(attrs={"id" : "m_ChooseTerm_term"}).findAll("option"):
		terms.append({
			"value" : row["value"],
			"year_string" : row.text,
			"current" : True if "selected" in row.attrs else False
		})

	information = {
		"name" : soup.find(attrs={"id" : "m_masterleftDiv"}).find(text=True).string.replace("\r\n", "").replace("\t","").strip(),
		"school_id" : str(config["school_id"]),
		"branch_id" : idGroups.group("branch_id") if not idGroups is None else "",
		"terms" : terms
	}

	return {
		"status" : "ok",
		"information" : information
	}

print school_info({"school_id" : 517})