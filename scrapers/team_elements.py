#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions
import urllib

def team_elements ( config, term = False ):
	teamElementList = []
	url = urls.team_elements.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{TEAM_ID}}", str(config["subject_id"])).replace("{{BRANCH_ID}}", str(config["branch_id"]))

	response = proxy.session.get(url)

	html = response.text

	soup = Soup(html)

	if not term == False:
		term = "&m%24ChooseTerm%24term=" + term
	else:
		term = ""

	firstViewState = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})

	eventValidationText = soup.find(id="aspnetForm").find(id="__EVENTVALIDATION")["value"]

	eventValidation = urllib.urlencode({"__EVENTVALIDATION" : eventValidationText})

	response = proxy.session.post(url, data="__EVENTTARGET=" + "m%24Content%24AktuelAndAfdelingCB%24ShowOnlyAktulleCB"+ firstViewState + "&" + eventValidation + term)

	html = response.text

	soup = Soup(html)

	if soup.find(attrs={"id" : "m_Content_AktuelAndAfdelingCB_ShowOnlyCurrentShoolAfdelingCB"}):
		firstViewState = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})

		eventValidationText = soup.find(id="aspnetForm").find(id="__EVENTVALIDATION")["value"]

		eventValidation = urllib.urlencode({"__EVENTVALIDATION" : eventValidationText})

		response = proxy.session.post(url, data="__EVENTTARGET=" + "m%24Content%24AktuelAndAfdelingCB%24ShowOnlyCurrentShoolAfdelingCB" + "&m%24Content%24AktuelAndAfdelingCB%24ShowOnlyCurrentShoolAfdelingCB=on&" + firstViewState + term + "&" + eventValidation )

		html = response.text

		soup = Soup(html)

	if soup.find("table", attrs={"id" : "m_Content_contenttbl"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	rows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

	idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy.aspx\?type=(?P<type_name>.*)&holdelementid=(?P<team_element_id>.*)")

	for row in rows:
		groups = idProg.match(row["href"])

		teamElementList.append({
			"name" : unicode(row.text),
			"team_element_id" : groups.group("team_element_id") if "team_element_id" in groups.groupdict() else "",
			"school_id" : config["school_id"],
			"branch_id" : config["branch_id"],
			"context_card_id" : "HE" + groups.group("team_element_id") if "team_element_id" in groups.groupdict() else ""
		})

	return {
		"status" : "ok",
		"team_elements" : teamElementList,
		"term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
	}