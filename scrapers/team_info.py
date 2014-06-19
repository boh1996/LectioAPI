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
import context_card

def team_info ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/aktivitet/AktivitetLinks.aspx?holdelementid=%s" % ( str(config["school_id"]), str(config["team_element_id"]) )

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

	if soup.find("div", attrs={"id" : "s_m_HeaderContent_subnavigator_generic_tr"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	#soup.find(attrs={"id" : "s_m_HeaderContent_MainTitle"}).find("div").decompose()

	nameProg = re.compile(ur"(?P<type>[.^\S]*) (?P<name>.*) - (.*)")
	nameGroups = nameProg.match(soup.find(attrs={"id" : "s_m_HeaderContent_MainTitle"}).text)
	contextCards = []
	contextCards.append(soup.find(attrs={"id" : "s_m_HeaderContent_MainTitle"})["lectiocontextcard"])
	teamType = "team" if "Holdet" in soup.find(attrs={"id" : "s_m_HeaderContent_MainTitle"}).text else "group"
	links = soup.find(attrs={"id" : "s_m_HeaderContent_subnavigator_generic_tr"}).findAll("a")
	teamIdProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/BD\/HoldReservations.aspx\?HoldID=(?P<team_id>.*)&prevurl=(?P<prev_url>.*)")
	if teamType == "team":
		teamIdGroups = teamIdProg.match(links[8]["href"])
	else:
		teamIdGroups = teamIdProg.match(links[6]["href"])
	teamObject = context_card.team({"school_id" : str(config["school_id"]), "context_card_id" : soup.find(attrs={"id" : "s_m_HeaderContent_MainTitle"})["lectiocontextcard"]}, session)

	if not teamIdGroups is None:
		contextCards.append("H" + teamIdGroups.group("team_id"))

	information = {
		"context_cards" : contextCards,
		"team_element_id" : str(config["team_element_id"]),
		"type" : teamType,
		"name" : nameGroups.group("name") if not nameGroups is None else "",
		"team_id" : teamIdGroups.group("team_id") if not teamIdGroups is None else "",
		"team" : teamObject["team"] if "team" in teamObject else "",
		"name_text" : soup.find(attrs={"id" : "s_m_HeaderContent_MainTitle"}).text
	}

	return {
		"status" : "ok",
		"information" : information
	}