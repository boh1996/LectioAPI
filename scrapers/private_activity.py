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

def private_activity ( config, session = False ):
	if session is False:
		session = authenticate.authenticate(config)

	if session == False:
		return {"status" : "error", "type" : "authenticate"}

	url = "https://www.lectio.dk/lectio/%s/privat_aftale.aspx?aftaleid=%s" % ( str(config["school_id"]), str(config["activity_id"]) )

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

	if soup.find("div", attrs={"id" : "m_Content_island1_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	studentProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/forside.aspx\?elevid=(?P<student_id>.*)")
	studentGroups = studentProg.match(soup.find("meta", attrs={"name" : "msapplication-starturl"})["content"])

	appointment = {
		"activity_id" : str(config["activity_id"]),
		"school_id" : str(config["school_id"]),
		"title" : unicode(soup.find("input", attrs={"id" : "m_Content_titelTextBox_tb"})["value"].replace("\r\n", "")),
		"comment" : unicode(soup.find("textarea", attrs={"id" : "m_Content_commentTextBox_tb"}).text.replace("\r\n", "")),
		"student_id" : studentGroups.group("student_id"),
		"start" : datetime.strptime("%s %s" % (soup.find("input", attrs={"id" : "m_Content_startdateCtrl__date_tb"})["value"], soup.find("input", attrs={"id" : "m_Content_startdateCtrl_startdateCtrl_time_tb"})["value"]), "%d/%m-%Y %H:%M"),
		"end" : datetime.strptime("%s %s" % (soup.find("input", attrs={"id" : "m_Content_enddateCtrl__date_tb"})["value"], soup.find("input", attrs={"id" : "m_Content_enddateCtrl_enddateCtrl_time_tb"})["value"]), "%d/%m-%Y %H:%M")
	}

	return {
		"status" : "ok",
		"appointment" : appointment
	}

print private_activity({
	"school_id" : 517,
	"student_id" : 4789793691,
	"username" : "boh1996",
	"password" : "jwn53yut",
	"branch_id" : "4733693427",
	"activity_id" : "9286743058"
})