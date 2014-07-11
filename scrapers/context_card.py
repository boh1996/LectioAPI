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
Group:
G5936111251
H5936111251
HE5936111268
'''

'''
Cards:
HE : Team Element
SR : Field of study
S : Student
U : User
T: Teacher
H : Team
XF : XPRS Subject
G : Group - Not Working
'''

def xprs_subject ( config ):
	url = "https://www.lectio.dk/lectio/%s/contextcard/contextcard.aspx?lectiocontextcard=%s" % ( str(config["school_id"]), str(config["context_card_id"]) )

	# Insert the session information from the auth function
	cookies = {
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

	level = "Unknown"

	if not codeGroups is None:
		level = "A" if "A" in codeGroups.group("code") else "B" if "B" in codeGroups.group("code") else "C"

	return {
		"status" : "ok",
		"xprs_subject" : {
			"name" : soup.find(attrs={"id" : "ctl00_Content_cctitle"}).text.replace("XPRS-fag - ", ""),
			"code" : codeGroups.group("code").replace("A", "").replace("B", "").replace("C", "") if not codeGroups is None else "",
			"subject_sub_type" : "none" if tables[1].findAll("td")[3].text == "Ingen underfag" else "differs" if tables[1].findAll("td")[3].text == "Variable underfag" else tables[1].findAll("td")[3].text,
			"context_card_id" : str(config["context_card_id"]),
			"level" : level,
			"xprs_subject_id" : str(config["context_card_id"]).replace("XF", ""),
			"code_full" : codeGroups.group("code") if not codeGroups is None else "",
			"notices" : tables[1].findAll("td")[5].text.split("\n"),
			"code_full_name" : tables[1].findAll("td")[1].text
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
		"school_id" : pictureGroups.group("school_id") if not pictureGroups is None else "",
		"context_card_id" : soup.find("img", attrs={"id" : "ctl00_Content_ImageCtrlthumbimage"})["lectiocontextcard"],
		"name" : nameGroups.group("name") if not nameGroups is None else "",
		"type" : userType,
	}

	if not soup.find("img", attrs={"id" : "ctl00_Content_ImageCtrlthumbimage"})["src"] == "/lectio/img/defaultfoto_small.jpg":
		user["picture_id"] = pictureGroups.group("picture_id") if not pictureGroups is None else ""

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

	cookies = {}

	if not session is False:
		if session == True:
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

	type = "team" if "Hold" in soup.find(attrs={"id" : "ctl00_Content_cctitle"}).text else "group"

	if type == "group":
		return group(config, session)

	name = str(soup.find(attrs={"id" : "ctl00_Content_cctitle"}).text.replace("Hold - ", "").strip().encode("utf8"))
	tables = soup.findAll("table")
	subject = unicode(tables[1].findAll("td")[1].text)
	teamElementProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy\.aspx\?type=holdelement&holdelementid=(?P<team_element_id>.*)")
	classProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy\.aspx\?type=(?P<type>.*)&klasseid=(?P<class_id>.*)")
	active = False
	teamElementGroups = None
	classGroups = None
	if not soup.find(attrs={"id" : "ctl00_Content_linksrep_ctl00_somelink"}) is None:
		active = True
		teamElementGroups = teamElementProg.match(soup.find(attrs={"id" : "ctl00_Content_linksrep_ctl00_somelink"})["href"])

	classes = []

	if len(soup.findAll("ul")) > 1:
		for row in soup.findAll("ul")[1].findAll("a"):
			classGroups = classProg.match(row["href"])
			classes.append({
				"name" : row.text.encode("utf8"),
				"class_id" : str(classGroups.group("class_id") if not classGroups is None else ""),
				"type" : "base_class" if  classGroups.group("type") == "stamklasse" and not classGroups is None else ""
			})

	team = {
		"name" : name,
		"subject" : subject,
		"active" : active,
		"school_id" : str(config["school_id"]),
		"team_element_id" : teamElementGroups.group("team_element_id") if not teamElementGroups is None else "",
		"context_card_id" : str(config["context_card_id"]),
		"classes" : classes,
		"type" : type
	}

	return {
		"status" : "ok",
		"team" : team
	}

# Team or Team Element
def group ( config, session = False ):
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

	type = "team" if "Hold" in soup.find(attrs={"id" : "ctl00_Content_cctitle"}).text else "group"

	if type == "team":
		return team(config, session)

	name = unicode(soup.find(attrs={"id" : "ctl00_Content_cctitle"}).text.replace("Gruppe - ", ""))
	tables = soup.findAll("table")
	teamElementProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy\.aspx\?type=holdelement&holdelementid=(?P<team_element_id>.*)")
	classProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy\.aspx\?type=(?P<type>.*)&klasseid=(?P<class_id>.*)")
	if not soup.find(attrs={"id" : "ctl00_Content_linksrep_ctl00_somelink"}) is None:
		teamElementGroups = teamElementProg.match(soup.find(attrs={"id" : "ctl00_Content_linksrep_ctl00_somelink"})["href"])

	classes = []

	if len(soup.findAll("ul")) > 1:
		for row in soup.findAll("ul")[1].findAll("a"):
			classGroups = classProg.match(row["href"])
			classes.append({
				"name" : row.text.encode("utf8"),
				"class_id" : classGroups.group("class_id") if not classGroups is None else "",
				"type" : "base_class" if  classGroups.group("type") == "stamklasse" and not classGroups is None else ""
			})


	team = {
		"name" : name,
		"school_id" : str(config["school_id"]),
		"team_element_id" : teamElementGroups.group("team_element_id") if not teamElementGroups is None else "",
		"context_card_id" : str(config["context_card_id"]),
		"classes" : classes
	}

	return {
		"status" : "ok",
		"team" : team
	}