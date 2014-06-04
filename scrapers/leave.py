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

# Set Leave - https://www.lectio.dk/lectio/517/fravaer_aarsag.aspx?elevid=4789793691&id=7436285108&atype=aa&prevurl=subnav%2ffravaerelev.aspx%3felevid%3d4789793691%26lectab%3daarsager
# Leave Reasons - https://www.lectio.dk/lectio/517/subnav/fravaerelev.aspx?elevid=4789793691&lectab=aarsager
# Leave numbers - https://www.lectio.dk/lectio/517/subnav/fravaerelev.aspx?elevid=4789793691&lectab=stud

def image ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/fravaer_billede.aspx?elevid=%s&year=%s&startdate=%s&enddate=%s" % ( str(config["school_id"]), str(config["student_id"]), str(config["year"]), config["start_date"].strftime("%d-%m-%Y"), config["end_date"].strftime("%d-%m-%Y") )

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

	return response.text

def leave ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/subnav/fravaerelev.aspx?elevid=%s" % ( str(config["school_id"]), str(config["student_id"]) )

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

	if soup.find("table", attrs={"id" : "s_m_Content_Content_SFTabStudentAbsenceDataTable"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_SFTabStudentAbsenceDataTable"}).findAll("tr")
	rows.pop(0)
	rows.pop(0)
	rows.pop(0)
	rows.pop(0)
	rows.pop(len(rows)-1)

	leaveRows = []
	teamIdProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/fravaer_elevhold.aspx\?holdelementid=(?P<team_element_id>.*)")
	leaveProg = re.compile(r"(?P<number>.*)\/(?P<modules>.*)")

	for row in rows:
		elements = row.findAll("td")
		teamIdGroups = teamIdProg.match(elements[0].find("a")["href"])
		periodeGroups = leaveProg.match(elements[2].text.replace(",", "."))
		calculatedGroups = leaveProg.match(elements[4].text.replace(",", "."))
		yearGroups = leaveProg.match(elements[6].text.replace(",", "."))

		writtenPeriodeGroups = leaveProg.match(elements[8].text.replace(",", "."))
		writtenCalculatedGroups = leaveProg.match(elements[10].text.replace(",", "."))
		writtenYearGroups = leaveProg.match(elements[12].text.replace(",", "."))
		data = {
       		"team" : {
       			"name": unicode(elements[0].find("a").text),
       			"team_id" : teamIdGroups.group("team_element_id") if not teamIdGroups is None else ""
       		},
       		"leave" : {
       			"period" : {
	       			"end_date" :  datetime.strptime(soup.find("input", attrs={"id" : "s_m_Content_Content_SFTabPeriodChooserCtrl_end__date_tb"})["value"], "%d/%m-%Y"),
	       			"start_date" :  datetime.strptime(soup.find("input", attrs={"id" : "s_m_Content_Content_SFTabPeriodChooserCtrl_start__date_tb"})["value"], "%d/%m-%Y"),
	       			"percent" : elements[1].text.replace(",", ".").replace("%", ""),
	       			"modules" : periodeGroups.group("modules") if not periodeGroups is None else "",
	       			"leave" : periodeGroups.group("number") if not periodeGroups is None else ""
	       		},
	       		"calculated" : {
	       			"percent" : elements[3].text.replace(",", ".").replace("%", ""),
	       			"modules" : calculatedGroups.group("modules") if not calculatedGroups is None else "",
	       			"leave" : calculatedGroups.group("number") if not calculatedGroups is None else ""
	       		},
	       		"year" : {
	       			"percent" : elements[5].text.replace(",", ".").replace("%", ""),
	       			"modules" : yearGroups.group("modules") if not yearGroups is None else "",
	       			"leave" : yearGroups.group("number") if not yearGroups is None else ""
	       		}
	       	},
	       	"written" : {
	       		"period" : {
	       			"end_date" :  datetime.strptime(soup.find("input", attrs={"id" : "s_m_Content_Content_SFTabPeriodChooserCtrl_end__date_tb"})["value"], "%d/%m-%Y"),
	       			"start_date" :  datetime.strptime(soup.find("input", attrs={"id" : "s_m_Content_Content_SFTabPeriodChooserCtrl_start__date_tb"})["value"], "%d/%m-%Y"),
	       			"percent" : elements[7].text.replace(",", ".").replace("%", ""),
	       			"hours" : writtenPeriodeGroups.group("modules") if not writtenPeriodeGroups is None else "",
	       			"leave" : writtenPeriodeGroups.group("number") if not writtenPeriodeGroups is None else ""
	       		},
	       		"calculated" : {
	       			"percent" : elements[9].text.replace(",", ".").replace("%", ""),
	       			"hours" : writtenCalculatedGroups.group("modules") if not writtenCalculatedGroups is None else "",
	       			"leave" : writtenCalculatedGroups.group("number") if not writtenCalculatedGroups is None else ""
	       		},
	       		"year" : {
	       			"percent" : elements[11].text.replace(",", ".").replace("%", ""),
	       			"hours" : writtenYearGroups.group("modules") if not writtenYearGroups is None else "",
	       			"leave" : writtenYearGroups.group("number") if not writtenYearGroups is None else ""
	       		}
	       	}
		}

		leaveRows.append(data)

	return {
		"status" : "ok",
		"leave" : leaveRows,
		"term" : {
       		"value" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
        	"years_string" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text,
        	"start_date" :  datetime.strptime(soup.find("input", attrs={"id" : "s_m_Content_Content_SFTabPeriodChooserCtrl_start__date_tb"})["value"], "%d/%m-%Y")
   		},
	}