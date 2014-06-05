from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
import proxy
from datetime import *
import re
import functions
import requests
import authenticate

def field_of_study ( config, session = False ):
	url = "https://www.lectio.dk/lectio/%s/studieretningElevValg.aspx?elevid=%s" % ( str(config["school_id"]), str(config["student_id"]) )

	if session == False:
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

	if soup.find("div", attrs={"id" : "s_m_Content_Content_id0_pa"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	elements = soup.find("div", attrs={"id" : "s_m_Content_Content_id0_pa"}).findAll("td")

	information = {
		"student_type" : elements[0].find("span").text,
		"student_start_term" : elements[1].find("span").text,
		"field_of_study" : {
			"name" : unicode(elements[2].find("span").text),
			"context_card_id" : elements[2].find("span")["lectiocontextcard"],
			"field_of_study_id" : elements[2].find("span")["lectiocontextcard"].replace("SR", "")
		},
		"student_id" : str(config["student_id"])
	}

	return {
		"status" : "ok",
		"information" : information
	}

def userinfo( config, session = False ):
	if session == False:
		session = authenticate.authenticate(config)

	if session == False:
		return {"status" : "error", "type" : "authenticate"}

	else:
		url = urls.front_page_url.replace("{{SCHOOL_ID}}", str(config["school_id"]))

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

		lectio_user_id = soup.find("div", attrs={"id" : "s_m_masterleftDiv"}).find("a")["href"]
		picture_id = soup.find("img", attrs={"id" : "s_m_HeaderContent_picctrlthumbimage"})["src"]
		teamRows = soup.find("div", attrs={"id" : "s_m_Content_Content_HoldAndGroupList"}).find("table").findAll("tr")

		teams = []
		buildInGroups = []
		ownGroups = []

		idProg = re.compile(r"\/lectio\/(?P<school_id>[0-9]*)/SkemaNy.aspx\?type=(?P<type_name>.*)&holdelementid=(?P<team_element_id>.*)")
		teamProg = re.compile(r"(?P<class_name>.*) (?P<team_name>.*)")

		# Teams
		for row in teamRows[0].findAll("td")[1].findAll("a"):
			idGroups = idProg.match(row["href"])
			name = row.text
			teamGroups = teamProg.match(name)
			teams.append({
				"id" : idGroups.group("team_element_id"),
				"class_name" : unicode(teamGroups.group("class_name")) if not teamGroups is None else "",
				"team_name" : unicode(teamGroups.group("team_name")) if not teamGroups is None else "",
				"name" : name
			})

		# Build in Groups
		for row in teamRows[1].findAll("td")[1].findAll("a"):
			idGroups = idProg.match(row["href"])
			name = row.text
			buildInGroups.append({
				"id" : idGroups.group("team_element_id"),
				"name" : name
			})

		# Own groups
		for row in teamRows[2].findAll("td")[1].findAll("a"):
			idGroups = idProg.match(row["href"])
			id = idGroups.group("team_element_id"),
			name = row.text
			ownGroups.append({
				"id" : id,
				"name" : name
			})

		# Student name
		name = re.sub(r'"Eleven (\w+), (\w+) - Forside"',r'\2',soup.find("div", attrs={"id" : "s_m_HeaderContent_MainTitle"}).text)

		# Info
		informations = []
		schoolTable = soup.find("table", attrs={"id" : "s_m_Content_Content_importantInfo"})
		examinations = []
		grades = []
		infoObjects = schoolTable.findAll("tr")
		dayTimeProg = re.compile(r"(?P<day>.*)/(?P<month>.*)-(?P<year>.*) (?P<hour>.*):(?P<minute>.*)")

		if not soup.find("table", attrs={"id" : "s_m_Content_Content_KaraktererInfo"}) is None:
			for row in soup.find("table", attrs={"id" : "s_m_Content_Content_KaraktererInfo"}).findAll("tr"):
				elements = row.findAll("td")
				gradeTeams = []
				gradeTeamProg = re.compile(r"(?P<class_name>.*) (?P<team_name>.*)")
				dayTimeGroups = dayTimeProg.match(elements[2]["title"])

				for gradeTeam in elements[1]["title"].replace("Frigives: ", "").split(", "):
					gradeTeamGroups = gradeTeamProg.match(gradeTeam)
					gradeTeams.append({
						"class_name" : unicode(gradeTeamGroups.group("class_name")) if not gradeTeamGroups is None else "",
						"team_name" : unicode(gradeTeamGroups.group("team_name")) if not gradeTeamGroups is None else ""
					})
				grades.append({
					"date" : datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dayTimeGroups.group("day")), functions.zeroPadding(dayTimeGroups.group("month")), dayTimeGroups.group("year"), dayTimeGroups.group("hour"), dayTimeGroups.group("minute")), "%d/%m-%Y %H:%M"),
					"teams" : gradeTeams
				})

		if not soup.find("table", attrs={"id" : "s_m_Content_Content_EksamenerInfo"}) is None:
			examObjects = soup.find("table", attrs={"id" : "s_m_Content_Content_EksamenerInfo"}).findAll("tr")
		else:
			examObjects = []

		examIdProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/proevehold.aspx\?type=proevehold&ProeveholdId=(?P<test_team_id>.*)&prevurl=forside.aspx")

		for row in examObjects:
			elements = row.findAll("td")
			examIdGroups = examIdProg.match(elements[1].find("a")["href"])
			dayTimeGroups = dayTimeProg.match(elements[2]["title"])
			examNameProg = re.compile(r"(?P<class_name>.*) (?P<team_name>.*) (?P<type_name>.*)\. eks\.")
			examNameGroups = examNameProg.match(unicode(elements[1].find("a").find("span").text))
			type_name = examNameGroups.group("type_name") if not examNameGroups is None else ""
			examinations.append({
				"test_team_id" : examIdGroups.group("test_team_id"),
				"school_id" : examIdGroups.group("school_id"),
				"title" : unicode(elements[1].find("a").find("span").text),
				"class_name" : examNameGroups.group("class_name") if not examNameGroups is None else "",
				"team_name" : examNameGroups.group("team_name") if not examNameGroups is None else "",
				"date" : datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(dayTimeGroups.group("day")), functions.zeroPadding(dayTimeGroups.group("month")), dayTimeGroups.group("year"), dayTimeGroups.group("hour"), dayTimeGroups.group("minute")), "%d/%m-%Y %H:%M")
			})

		if not infoObjects is None:
			for info in infoObjects:
				infoType = ""
				tds = info.findAll("td")
				if tds[0]["class"] is None or not tds[0]["class"] is None and not "norecord" in tds[0]["class"]:
					if  tds[0].find("img")["src"] == "/lectio/img/prio1.auto" :
						infoType = "red"
					elif tds[0].find("img")["src"] == "/lectio/img/prio2.auto":
						infoType = "yellow"
					elif tds[0].find("img")["src"] == "/lectio/img/prio3.auto":
						infoType = "grey"
					informations.append({
						"text" : tds[1].find("span").text,
						"type" : infoType
					})

		nameProg = re.compile(r"Eleven (?P<name>.*), (?P<class_name>.*) - Forside")
		nameGroups = nameProg.match(name)

		return {
			"status" : "ok",
			"lectio_user_id" : lectio_user_id.replace("/lectio/%s/SkemaNy.aspx?type=elev&elevid=" % (str(config["school_id"])), ""),
			"lectio_picture_id" : picture_id.replace("/lectio/%s/GetImage.aspx?pictureid=" % (str(config["school_id"])), ""),
			"teams" : teams,
			"buildInGroups" : buildInGroups,
			"ownGroups" : ownGroups,
			"name" : unicode(nameGroups.group("name")) if not nameGroups is None else "",
			"class_name" : nameGroups.group("class_name") if not nameGroups is None else "",
			"information" : informations,
			"examinations" : examinations,
			"grades" : grades
		}