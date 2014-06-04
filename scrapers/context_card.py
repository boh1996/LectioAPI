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

#XPRS subject
# https://www.lectio.dk/lectio/517/contextcard/contextcard.aspx?lectiocontextcard=XF1453150703
# Team Element
# https://www.lectio.dk/lectio/517/contextcard/contextcard.aspx?lectiocontextcard=HE5936223706
# Field of Study - SR5203467258
# https://www.lectio.dk/lectio/517/contextcard/contextcard.aspx?lectiocontextcard=SR5203467258&prevurl=studieretningElevValg.aspx%3Felevid%3D4789793691&ignoreUnsupportedIdTypes=0

def user ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/contextcard/contextcard.aspx?lectiocontextcard=%s" % ( str(config["school_id"]), str(config["context_card_id"]) )

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

	if soup.find("span", attrs={"id" : "ctl00_Content_cctitle"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	title = soup.find("span", attrs={"id" : "ctl00_Content_cctitle"}).text

	userType = "student" if "Elev" in title else "teacher"

	nameProg = re.compile(r"(?P<type>.*) - (?P<name>.*)")
	nameGroups = nameProg.match(title)

	pictureProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/GetImage.aspx\?pictureid=(?P<picture_id>.*)")
	pictureGroups = pictureProg.match(soup.find("img", attrs={"id" : "ctl00_Content_ImageCtrlthumbimage"})["src"])

	user = {
		"picture_id" : pictureGroups.group("picture_id") if not pictureGroups is None else "",
		"school_id" : pictureGroups.group("school_id") if not pictureGroups is None else "",
		"context_card_id" : soup.find("img", attrs={"id" : "ctl00_Content_ImageCtrlthumbimage"})["lectiocontextcard"],
		"name" : nameGroups.group("name") if not nameGroups is None else "",
		"type" : userType,
	}

	elements = soup.findAll("table")[1].findAll("td")

	if userType == "student":
		user["student_id"] = soup.find("img", attrs={"id" : "ctl00_Content_ImageCtrlthumbimage"})["lectiocontextcard"].replace("S", "")
		user["class_name"] = unicode(elements[1].text)
	else:
		teamProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy.aspx\?type=(?P<type>.*)&holdelementid=(?P<team_element_id>.*)")
		user["teacher_id"] = soup.find("img", attrs={"id" : "ctl00_Content_ImageCtrlthumbimage"})["lectiocontextcard"].replace("T", "")

		teams = []

		if len(elements) > 1:
			for row in elements[1].findAll("a"):
				teamGroups = teamProg.match(row["href"])
				teams.append({
					"name" : unicode(row.text),
					"school_id" : teamGroups.group("school_id") if not teamGroups is None else "",
					"team_element_id" : teamGroups.group("team_element_id") if not teamGroups is None else ""
				})

		user["teams"] = teams
	return {
		"status" : "ok",
		"user" : user
	}