#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
import functions

def xprs_subjects ( start, end, increase , school_id, checkLevels = False, levels = ["01", "02", "03", "04", "05", "06"] ):

	subjects = []

	cards = []

	for code in range(0, end-start+1):

		if checkLevels == False:
			cards.append(start + (code*increase))
		else:
			codeKey = start + (code*increase)
			for row in levels:
				cards.append(str(codeKey)+row)

	for code in cards:

		url = "https://www.lectio.dk/lectio/%s/contextcard/contextcard.aspx?lectiocontextcard=XF%s" % ( str(school_id), str(code) )

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

			codeProg = re.compile(r"(?P<code>[.^\S]*) (?P<name>.*)")

			if not soup.find("span", attrs={"id" : "ctl00_Content_cctitle"}) is None:

				notices = []

				tables = soup.findAll("table")

				codeGroups = codeProg.match(tables[1].findAll("td")[1].text)

				level = "Unkmown"

				if not codeGroups is None:
					level = "A" if "A" in codeGroups.group("code") else "B" if "B" in codeGroups.group("code") else "C"

				subjects.append({
					"name" : unicode(soup.find(attrs={"id" : "ctl00_Content_cctitle"}).text.replace("XPRS-fag - ", "")),
					"code" : codeGroups.group("code").replace("A", "").replace("B", "").replace("C", "") if not codeGroups is None else "",
					"subject_sub_type" : "none" if tables[1].findAll("td")[3].text == "Ingen underfag" else "differs" if tables[1].findAll("td")[3].text == "Variable underfag" else tables[1].findAll("td")[3].text,
					"context_card_id" : "XF" + str(code),
					"level" : level,
					"code_full" : codeGroups.group("code") if not codeGroups is None else "",
					"xprs_subject_id" : str(code),
					"notices" : tables[1].findAll("td")[5].text.split("\n"),
					"code_full_name" : tables[1].findAll("td")[1].text
				})

			else:
				print code

	return subjects

# Caution, 403 Ahead
#subjects = []
#subjects = subjects + xprs_subjects(7000, 7019,1, 517, True, ["01", "02"])
#subjects = subjects + xprs_subjects(1453150702, 1453150867,1, 517, False)
#subjects = subjects + xprs_subjects(1453150702, 1453150706,1, 517, False)
#subjects = subjects + xprs_subjects(6043, 6048,1, 517, True, ["01"])

#f = open("log.txt", "w")

#print >> f, subjects