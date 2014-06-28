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
import authenticate

def group_members ( config, session = False ):
	if session == False:
		url = "https://www.lectio.dk/lectio/%s/subnav/members.aspx?holdelementid=%s&showteachers=1&showstudents=1&reporttype=std" % ( str(config["school_id"]), str(config["team_element_id"]) )
		cookies = {}
	else:
		if session == True:
			session = authenticate.authenticate(config)
		url = "https://www.lectio.dk/lectio/%s/subnav/members.aspx?holdelementid=%s&showteachers=1&showstudents=1" % ( str(config["school_id"]), str(config["team_element_id"]) )
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

	if soup.find("table", attrs={"id" : "s_m_Content_Content_laerereleverpanel_alm_gv"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	headers = []
	for header in soup.find("table", attrs={"id" : "s_m_Content_Content_laerereleverpanel_alm_gv"}).find("tr").findAll("th"):
		headers.append(header.text)

	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_laerereleverpanel_alm_gv"}).findAll("tr")
	rows.pop(0)

	objectList = []

	for row in rows:
		elements = row.findAll("td")

		if unicode(headers[0]) == u"Type":
			person_type = "teacher" if unicode(elements[0].text) == u"Lærer" else "student"

			context_card_id = elements[2]["lectiocontextcard"]

			if person_type == "teacher":
				person_id = context_card_id.replace("T", "")
			else:
					person_id = context_card_id.replace("S", "")

			data = {
				"type" : person_type,
				"person_text_id" : elements[1].text,
				"first_name" : elements[2].text.replace("\n", " ").strip().encode("utf8"),
				"last_name" : elements[3].text.replace("\n", " ").strip().encode("utf8"),
				"full_name" : elements[2].text.replace("\n", " ").strip().encode("utf8") + " " + elements[3].text.replace("\n", " ").strip().encode("utf8"),
				"context_card_id" : context_card_id,
				"person_id" : person_id
			}

			if unicode(headers[len(headers)-1]) == "Studieretning" and person_type == "student":
				data["field_of_study"] = {
					"name" : elements[4].find("span").text.encode("utf8"),
					"context_card_id" : elements[4].find("span")["lectiocontextcard"],
					"field_of_study_id" : elements[4].find("span")["lectiocontextcard"].replace("SR", "")
				}

			objectList.append(data)
		else:
			photoProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/GetImage.aspx\?pictureid=(?P<picture_id>.*)")
			photoGroups = photoProg.match(elements[0].find("img")["src"])

			person_type = "teacher" if unicode(elements[1].text) == u"Lærer" else "student"

			context_card_id = elements[3]["lectiocontextcard"]

			if person_type == "teacher":
				person_id = context_card_id.replace("T", "")
			else:
				person_id = context_card_id.replace("S", "")

			data = {
				"type" : person_type,
				"person_text_id" : elements[2].text,
				"first_name" : unicode(elements[3].text).replace("\n", " ").strip().encode("utf8"),
				"last_name" : unicode(elements[4].text).replace("\n", " ").strip().encode("utf8"),
				"full_name" : unicode(elements[3].text.replace("\n", " ").strip() + " " + elements[4].text.replace("\n", " ").strip()).encode("utf8").strip(),
				"context_card_id" : context_card_id,
				"person_id" : person_id,
				"picture_id" : photoGroups.group("picture_id")
			}

			if unicode(headers[len(headers)-1]) == "Studieretning" and person_type == "student":
				data["field_of_study"] = {
					"name" : unicode(elements[5].find("span").text).encode("utf8"),
					"context_card_id" : elements[5].find("span")["lectiocontextcard"],
					"field_of_study_id" : elements[5].find("span")["lectiocontextcard"].replace("SR", "")
				}

			objectList.append(data)
	return {
		"status" : "ok",
		"objects" : objectList
	}