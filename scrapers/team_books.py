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
import authenticate

def team_books ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/BD/HoldReservations.aspx?HoldID=%s" % ( str(config["school_id"]), str(config["team_id"]) )

	if session is False:
		session = authenticate.authenticate(config)

	if session == False:
		return {"status" : "error", "type" : "authenticate"}
	# Insert the session information from the auth function
	cookies = {
		"lecmobile" : "0",
		"ASP.NET_SessionId" : session["ASP.NET_SessionId"],
		"LastLoginUserName" : session["LastLoginUserName"],
		"lectiogsc" : session["lectiogsc"],
		"LectioTicket" : session["LectioTicket"]
	}

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

	if soup.find("div", attrs={"id" : "m_Content_ebooks_island_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	books = []

	for row in soup.find(attrs={"id" : "m_Content_ebooks_island_pa"}).find("table").findAll("tr")[1:]:
		elements = row.findAll("td")
		books.append({
			"team_id" : str(config["team_id"]),
			"type" : "ebook",
			"title" : unicode(elements[0].text.replace("\r\n", "").replace("\t", "")),
			"read" : unicode(elements[1].text.replace("\r\n", "").replace("\t", ""))
		})

	for row in soup.find(attrs={"id" : "m_Content_reservationsStudentGV"}).findAll("tr")[1:]:
		elements = row.findAll("td")

		books.append({
			"type" : "book",
			"team_id" : str(config["team_id"]),
			"title" : unicode(elements[0].text.replace("\r\n", "").replace("\t", ""))
		})

	return {
		"status" : "ok",
		'books' : books
	}