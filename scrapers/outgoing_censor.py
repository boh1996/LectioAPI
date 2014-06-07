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

def outgoing_censor ( config ):
	url = "https://www.lectio.dk/lectio/%s/proevehold.aspx?type=udgcensur&outboundCensorID=%s" % ( str(config["school_id"]), str(config["outgoing_censor_id"]) )

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

	if soup.find("div", attrs={"id" : "m_Content_LectioDetailIslandProevehold_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	teacherProg = re.compile(r"(?P<name>.*) \((?P<abbrevation>.*)\)")
	teacherGroups = teacherProg.match(soup.find("td", attrs={"id" : "m_Content_outboundcensor_teachername"}).text)

	return {
		"status" : "ok",
		"teacher" : {
			"name" : teacherGroups.group("name") if not teacherGroups is None else unicode(soup.find("td", attrs={"id" : "m_Content_outboundcensor_teachername"}).text),
			"abbrevation" : teacherGroups.group("abbrevation") if not teacherGroups is None else ""
		},
		"test_team" : unicode(soup.find("td", attrs={"id" : "m_Content_outboundcensor_proeveholdname"}).text),
		"insitution" : unicode(soup.find("td", attrs={"id" : "m_Content_outboundcensor_institution"}).text),
		"xprs_test" : unicode(soup.find("td", attrs={"id" : "m_Content_outboundcensor_xprsproeve"}).text),
		"numberof_students" : soup.find("td", attrs={"id" : "m_Content_outboundcensor_elevtal"}).text,
		"note" : unicode(soup.find("td", attrs={"id" : "m_Content_outboundcensor_bemaerkning"}).text)
	}