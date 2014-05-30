#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def school_state ( config ):
	url = urls.teams.replace("{{SCHOOL_ID}}", str(config["school_id"]))

	response = proxy.session.get(url)

	html = response.text

	soup = Soup(html)

	if not soup.find("div", attrs={"id" : "m_Content_alertBox_alerts"}) is None:
		message = soup.find("div", attrs={"id" : "m_Content_alertBox_alerts"}).find("div").text
		return {
			"status" : "ok",
			"state" : "not_in_use" if message == "Skolen er ikke i brug." else "other"
		}
	else:
		return {
			"status" : "ok",
			"state" : "ok"
		}