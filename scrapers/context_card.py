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

'''
Cards:
HE : Team Element
SR : Field of study
S : Student
U : User
T: Teacher
H : Team
XF : XPRS Subject
'''

def xprs_subject ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/contextcard/contextcard.aspx?lectiocontextcard=%s" % ( str(config["school_id"]), str(config["context_card_id"]) )

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

	if soup.find("span", attrs={"id" : "ctl00_Content_cctitle"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	tables = soup.findAll("table")

	codeProg = re.compile(r"(?P<code>[.^\S]*) (?P<name>.*)")
	codeGroups = codeProg.match(tables[1].findAll("td")[1].text)

	level = "Unkmown"

	if not codeGroups is None:
		level = "A" if "A" in codeGroups.group("code") else "B" if "B" in codeGroups.group("code") else "C"

	return {
		"status" : "ok",
		"xprs_subject" : {
			"name" : soup.find(attrs={"id" : "ctl00_Content_cctitle"}).text.replace("XPRS-fag - ", ""),
			"code" : codeGroups.group("code").replace("A", "").replace("B", "").replace("C", "") if not codeGroups is None else "",
			"subject_sub_type" : "none" if tables[1].findAll("td")[3].text == "Ingen underfag" else tables[1].findAll("td")[3].text,
			"context_card_id" : str(config["context_card_id"]),
			"level" : level,
			"code_full" : codeGroups.group("code") if not codeGroups is None else ""
		}
	}

def user ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/contextcard/contextcard.aspx?lectiocontextcard=%s" % ( str(config["school_id"]), str(config["context_card_id"]) )

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

def field_of_study ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/contextcard/contextcard.aspx?lectiocontextcard=%s" % ( str(config["school_id"]), str(config["context_card_id"]) )

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

	if soup.find("span", attrs={"id" : "ctl00_Content_cctitle"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	tables = soup.findAll("table")
	idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/studieretningSe.aspx\?sid=(?P<field_of_study_id>.*)")
	idGroups = idProg.match(soup.find(attrs={"id" : "ctl00_Content_linksrep_ctl00_somelink"})["href"])

	return {
		"status" : "ok",
		"field_of_study" : {
			"name" : unicode(tables[1].findAll("td")[1].text),
			"field_of_study_id" : idGroups.group("field_of_study_id") if not idGroups is None else "",
			"school_id" : str(config["school_id"]),
			"context_card_id" : str(config["context_card_id"])
		}
 	}

# Team or Team Element
def team ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/contextcard/contextcard.aspx?lectiocontextcard=%s" % ( str(config["school_id"]), str(config["context_card_id"]) )

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

	if soup.find("span", attrs={"id" : "ctl00_Content_cctitle"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	name = unicode(soup.find(attrs={"id" : "ctl00_Content_cctitle"}).text.replace("Hold - ", ""))
	tables = soup.findAll("table")
	subject = unicode(tables[1].findAll("td")[1].text)
	teamElementProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy\.aspx\?type=holdelement&holdelementid=(?P<team_element_id>.*)")
	classProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy\.aspx\?type=stamklasse&klasseid=(?P<class_id>.*)")
	active = False
	teamElementGroups = None
	classGroups = None
	if not soup.find(attrs={"id" : "ctl00_Content_linksrep_ctl00_somelink"}) is None:
		active = True
		teamElementGroups = teamElementProg.match(soup.find(attrs={"id" : "ctl00_Content_linksrep_ctl00_somelink"})["href"])

	if not soup.find(attrs={"id" : "ctl00_Content_otherlinksrep_ctl00_somelink"}) is None:
		classGroups = classProg.match(soup.find(attrs={"id" : "ctl00_Content_otherlinksrep_ctl00_somelink"})["href"])

	team = {
		"name" : name,
		"subject" : subject,
		"active" : active,
		"school_id" : str(config["school_id"]),
		"team_element_id" : teamElementGroups.group("team_element_id") if not teamElementGroups is None else "",
		"context_card_id" : str(config["context_card_id"]),
		"class_id" : classGroups.group("class_id") if not classGroups is None else ""
	}

	return {
		"status" : "ok",
		"team" : team
	}