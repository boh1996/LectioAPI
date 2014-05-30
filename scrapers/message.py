#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import time
from time import mktime
import values
import codecs
import functions
import authenticate
import context_card

def message ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/beskeder2.aspx?type=liste&elevid=%s" % ( str(config["school_id"]), str(config["student_id"]) )

	if session is False:
		session = authenticate.authenticate(config)

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

	viewStateX = soup.find("input", attrs={"id" : "__VIEWSTATEX"})["value"]

	settings = {
		"__EVENTTARGET" : "__Page",
		"__EVENTARGUMENT" : "$LB2$_MC_$_%s" % ( str(config["thread_id"]) ),
		"__VIEWSTATEX" : viewStateX,
	}

	response = proxy.session.post(url, data=settings, headers=headers)

	html = response.text

	soup = Soup(html)

	if soup.find("div", attrs={"id" : "s_m_Content_Content_ViewThreadPagePanel"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	flagged = False if soup.find("input", attrs={"id" : "s_m_Content_Content_FlagThisThreadBox"})["src"] == "/lectio/img/flagoff.gif" else True

	originalElements = soup.find("table", attrs={"class" : "ShowMessageRecipients"}).findAll("td")

	#elements 6 - Sender
	#elements 9 - Recipients

	originalSenderUser = context_card.user({
		"context_card_id" : originalElements[8].find("span")["lectiocontextcard"],
		"school_id" : config["school_id"]
	}, session)

	originalSenderUser["user"]["user_context_card_id"] = originalElements[8].find("span")["lectiocontextcard"]
	originalSenderUser["user"]["person_id"] = originalElements[8].find("span")["lectiocontextcard"].replace("U", "")

	originalSubject = unicode(functions.cleanText(originalElements[2].text))

	messageInfo = {
		"original_subject" : originalSubject,
		"flagged" : flagged,
		"original_sender" : originalSenderUser
	}

	return {
		"status" : "ok",
		"message" : messageInfo,
	}

