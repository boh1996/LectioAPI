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

def leave_reasons ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/subnav/fravaerelev.aspx?elevid=%s&lectab=aarsager" % ( str(config["school_id"]), str(config["student_id"]) )

	if session is False:
		session = authenticate.authenticate(config)

	if session == False:
		return {"status" : "error", "type" : "authenticate"}

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

	if soup.find("table", attrs={"id" : "s_m_Content_Content_FatabAbsenceFravaerGV"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	missing = []
	reasons = []

	reasonKeys = {
		u"Andet" : "other",
		u"Kom for sent" : "too_late",
		u"Skolerelaterede aktiviteter" : "school_related",
		u"Private forhold" : "private",
		u"Sygdom" : "sick"
	}

	# TODO: Add Missing
	if soup.find(attrs={"id" : "s_m_Content_Content_FatabMissingAarsagerGV"}).find(attrs={"class" : "noRecord"}) is None:
		print "missing"

	if soup.find(attrs={"id" : "s_m_Content_Content_FatabAbsenceFravaerGV"}).find(attrs={"class" : "noRecord"}) is None:
		rows = soup.find(attrs={"id" : "s_m_Content_Content_FatabAbsenceFravaerGV"}).findAll("tr")
		rows.pop(0)

		activityProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/aktivitet\/aktivitetinfo.aspx\?id=(?P<activity_id>.*)&prevurl=(?P<prev_url>.*)")
		datetimeProg = re.compile(r"(?P<day>.*)\/(?P<month>.*)-(?P<year>.*) (?P<time>.*)")

		for row in rows:
			elements = row.findAll("td")
			activityGroups = activityProg.match(elements[2].find("a")["href"])
			dateGroups = datetimeProg.match(elements[5].find("span").text.strip().replace("\r\n", "").replace("\t", ""))
			reasons.append({
				"type" : "lesson" if elements[0].text.strip().replace("\r\n", "").replace("\t", "") == "Lektion" else "other",
				"week" : elements[1].text.strip().replace("\r\n", "").replace("\t", ""),
				"activity_id" : activityGroups.group("activity_id") if not activityGroups is None else "",
				"leave" : elements[3].text.strip().replace("\r\n", "").replace("\t", "").replace("%", ""),
				"creadited" :True if elements[4].text.strip().replace("\r\n", "").replace("\t", "") == "Ja" else False,
				"registred" : datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(dateGroups.group("day")), functions.zeroPadding(dateGroups.group("month")), dateGroups.group("year"), dateGroups.group("time")), "%d/%m-%Y %H:%M"),
				"teacher" : {
					"abbrevation" : unicode(elements[6].text.strip().replace("\r\n", "").replace("\t", ""))
				},
				"team" : {
					"name" : unicode(elements[7].text.strip().replace("\r\n", "").replace("\t", ""))
				},
				"comment" : unicode(elements[8].text.strip().replace("\r\n", "").replace("\t", "")),
				"reason" : {
					"value" : unicode(elements[9].text.strip().replace("\r\n", "").replace("\t", "")),
					"key" : reasonKeys[unicode(elements[9].text.strip().replace("\r\n", "").replace("\t", ""))] if unicode(elements[9].text.strip().replace("\r\n", "").replace("\t", "")) in reasonKeys else "other",
					"note": unicode(elements[10].text.strip().replace("\r\n", "").replace("\t", ""))
				},

			})

	return {
		"status" : "ok",
		"reasons" : reasons,
		"missing" : missing
	}