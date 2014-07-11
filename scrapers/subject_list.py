#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
import functions

def subject_list ( start, end, school_id ):
	increase = 1
	subjects = []

	cards = []

	for code in range(0, end-start+1):
		cards.append(start + (code*increase))

	for code in cards:
		url = "http://www.lectio.dk/lectio/%s/FindSkema.aspx?type=hold&fag=%s" % ( str(school_id), str(code) )

		cookies = {}

		# Insert User-agent headers and the cookie information
		headers = {
			"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
			"Content-Type" : "application/x-www-form-urlencoded",
			"Host" : "www.lectio.dk",
			"Origin" : "https://www.lectio.dk",
			"Cookie" : functions.implode(cookies, "{{index}}={{value}}", "; ")
		}
		error = False
		try:
			response = proxy.session.get(url, headers=headers)
		except Exception, e:
			print code
			error = True

		if error == False:
			html = response.text

			soup = Soup(html)

			if not soup.find("table", attrs={"id" : "m_Content_contenttbl"}) is None:
				elements = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).find("span").text.split(" - ")

				subjects.append({
					"abbrevation" : elements[0].encode("utf8"),
					"name" : elements[1].encode("utf8"),
					"subject_id" : str(code)
				})

	return subjects