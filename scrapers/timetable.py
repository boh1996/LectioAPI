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

#s2module-bg s2time-off

def sameDay ( date, dayOfWeek, week, year ):
	theDay = datetime.fromtimestamp(mktime(time.strptime("%s %s %s %s %s" % ("12", "00", dayOfWeek , week, year),"%H %M %w %W %Y")))
	return theDay.date() == date.date()

def timetable( config, url, week, year, session = False ):
	if session == False:
		cookies = {}
	else:
		if session == True:
			session = authenticate.authenticate(config)

		# Insert the session information from the auth function
		cookies = {
			"lecmobile" : "0",
			"ASP.NET_SessionId" : session["ASP.NET_SessionId"],
			"LastLoginUserName" : session["LastLoginUserName"],
			"lectiogsc" : session["lectiogsc"],
			"LectioTicket" : session["LectioTicket"]
		}

	# Sorting settings
	settings = {

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

	if soup.find("table", attrs={"id" : "s_m_Content_Content_SkemaNyMedNavigation_skema_skematabel"}) is None:
		return {
			"status" : False,
			"error" : "Data not found"
		}

	# Fetch all rows in the table
	rows = soup.find("table", attrs={"id" : "s_m_Content_Content_SkemaNyMedNavigation_skema_skematabel"}).findAll("tr")

	# Fetch module info, to make it possible to draw a complete timetable
	moduleInfo = []
	moduleInfoProg = re.compile(r"(?P<module_number>.*)\. (?P<start_time>.*) - (?P<end_time>.*)")

	for row in soup.findAll("div", attrs={"class" : "s2module-info"}):
		moduleInfoGroups = moduleInfoProg.match(row.text.strip().replace("modul", ""))
		if not moduleInfoGroups is None:
			start = moduleInfoGroups.group("start_time")
			if len(start) < 5:
				start = "0" + start

			end = moduleInfoGroups.group("end_time")
			if len(end) < 5:
				end = "0" + end
			moduleInfo.append({
				"module" : moduleInfoGroups.group("module_number"),
				"start" : start,
				"end" : end
			})

	# Fetch the general information celss
	generalInformationDays = rows[2].findAll("td")
	generalInformation = []

	holidayElements = []

	# Loop through all the cells, and look for information
	index = 0
	for tdRow in generalInformationDays:
		index = index+1
		if index > 1:
			row = tdRow.findAll("a")

			# Loop over the link elements, in the cell
			if not row == None and len(row) > 0:
				for element in row:

					# The time module uses "0" as the first week of the year
					if int(week) == 1:
						timeWeek = 0
					else:
						# Subtract one, because 0 is the first week
						timeWeek = int(week)-1

					dayOfWeek = index-1
					date = time.strptime("%s %s %s" % (str(dayOfWeek),str(timeWeek), str(year)),"%w %W %Y")
					content = element.find("div", attrs={"class" : "s2skemabrikcontent"}).findAll("span")[1]
					div = element.find("div", attrs={"class" : "s2skemabrikcontent"})

					href = None
					# If the a tag has a href, fetch it
					try:
						href = element["href"]
					except BaseException:
						pass

					if href == None:
						generalInformation.append({
							"message" : unicode(content.text),
							"date" : datetime.fromtimestamp(mktime(date)),
							"school_id" : str(config["school_id"]),
							"branch_id" : str(config["branch_id"]),
							"term" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
							"week" : week,
							"year" : year
						})
					else:
						# Compile the regular expression
						prog = re.compile(r"\/lectio\/(?P<school_id>[0-9]*)\/aktivitet\/aktivitetinfo.aspx\?id=(?P<activity_id>[0-9]*)&(?P<prev_url>.*)")
						activityGroups = prog.match(element["href"])
						generalInformation.append({
							"message" : unicode(content.text),
							"activity_id" : activityGroups.group("activity_id"),
							"status" : "changed" if "s2changed" in div["class"] else "cancelled" if "s2cancelled" in div["class"] else "normal",
							"date" : datetime.fromtimestamp(mktime(date)),
							"school_id" : str(config["school_id"]),
							"branch_id" : str(config["branch_id"]),
							"term" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
							"week" : week,
							"year" : year
						})

	# Find all the day elements
	timeElements = []


	headers = []

	headerRows = rows[1].findAll("td")
	headerRows.pop(0)
	headerProg = re.compile(ur"(?P<day_name>.*) \((?P<day>.*)\/(?P<month>.*)\)")

	for row in headerRows:
		headerGroups = headerProg.match(row.text)
		headerYear = year

		if not headerGroups is None:
			if int(week) == 1 and int(headerGroups.group("month")) == 12:
				headerYear = str(int(year) - 1)

			headers.append({
				"day" : headerGroups.group("day_name"),
				"date" : datetime.strptime("%s-%s-%s %s" % (functions.zeroPadding(headerGroups.group("day")), functions.zeroPadding(headerGroups.group("month")), headerYear, "12:00"), "%d-%m-%Y %H:%M")
			})

	dayElements = rows[3].findAll("td")
	dayElements.pop(0)

	# Loop over the days
	index = 0
	dayOfWeek = 1
	for dayElement in dayElements:
		# Increment the day
		index = index+1

		dayOfWeek = index-1

		# The time module uses "0" as the first week of the year
		if int(week) == 1:
			timeWeek = 0
		else:
			# Subtract one, because 0 is the first week
			timeWeek = int(week)-1

		# Find all the "a" tags, representing timetable elements
		timetableElements = dayElement.findAll("a")

		moduleIndex = 1

		for checkElement in dayElement.findAll(attrs={"class" : "s2module-bg"}):
			if "s2time-off" in checkElement["class"]:
				# Get time from module info elements
				holidayElements.append({
					"start" : datetime.strptime("%s-%s-%s %s" % (headers[index-1]["date"].strftime("%d"), headers[index-1]["date"].strftime("%m"), headers[index-1]["date"].strftime("%Y"), moduleInfo[moduleIndex-1]["start"]), "%d-%m-%Y %H:%M"),
					"end" : datetime.strptime("%s-%s-%s %s" % (headers[index-1]["date"].strftime("%d"), headers[index-1]["date"].strftime("%m"), headers[index-1]["date"].strftime("%Y"), moduleInfo[moduleIndex-1]["end"]), "%d-%m-%Y %H:%M")
				})
			moduleIndex = moduleIndex + 1

		# Loop over the timetable elements
		for timetableElement in timetableElements:

			#The type of the event, "private" or "school"
			type = None

			# Locate the different types of information in the url, and find the different RegEx groups
			expressions = [
				{"type" : "private", "expression" : r"\/lectio\/(?P<school_id>[0-9]*)\/privat_aftale.aspx\?aftaleid=(?P<activity_id>[0-9]*)"},
				{"type" : "school",  "expression" : r"\/lectio\/(?P<school_id>[0-9]*)\/aktivitet\/aktivitetinfo.aspx\?id=(?P<activity_id>[0-9]*)&(?P<prev_url>.*)"},
				{"type" : "outgoing_censor", "expression" : r"\/lectio\/(?P<school_id>.*)\/proevehold.aspx\?type=udgcensur&outboundCensorID=(?P<outbound_censor_id>.*)&prevurl=(?P<prev_url>.*)"},
				{"type" : "exam", "expression" : r"\/lectio\/(?P<school_id>.*)\/proevehold.aspx\?type=proevehold&ProeveholdId=(?P<test_team_id>.*)&prevurl=(?P<prev_url>.*)"}
			]

			# Loop over the expressions
			groups = []
			type = "other"
			for expressionObject in expressions:
				prog = re.compile(expressionObject["expression"])
				if prog.match(timetableElement["href"]):
					groups = prog.match(timetableElement["href"])
					type = expressionObject["type"]

			# Locate the status div
			div = timetableElement.find("div", attrs={"class" : "s2skemabrikcontent"})

			# A list of the teachers
			teachers = []

			# A list of the assigned teams
			teams = []

			# Find all the info span elements
			infoSpanObjects = timetableElement.findAll("span")

			# Loop over the Info spans
			for span in infoSpanObjects:
				id = None

				# Test if property exists
				try:
					id = span["lectiocontextcard"]
				except BaseException:
					pass

				if not id == None:
					 # Team
					if span["lectiocontextcard"][0] == "H":
						# Append the team
						teams.append({
							"context_card_id" : span["lectiocontextcard"],
							"title" : unicode(span.text),
							"team_id" : span["lectiocontextcard"].replace("HE", "")
						})
					# Teacher
					elif span["lectiocontextcard"][0] == "T":
						teachers.append({
							"abbrevation" : unicode(span.text),
							"context_card_id" : span["lectiocontextcard"],
							"teacher_id" : span["lectiocontextcard"].replace("T", "")
						})

			# Get the titletext where to extract start and end times from
			title = timetableElement["title"]

			# Match the title, to extract the start and end time
			timeProg = re.compile(r"(?P<start_hour>[0-9]*):(?P<start_minute>[0-9]*) til (?P<end_hour>[0-9]*):(?P<end_minute>[0-9]*)")
			timeGroups = timeProg.search(unicode(title).encode("utf8"), re.MULTILINE)

			# Get the "main sections" separated by a double return \n\n
			mainSections = title.split("\n\n")

			# Grab the top section and split it by a single return \n
			topSection = mainSections[0].split("\n")

			# Initialize variables, assume that nothing is cancelled or changed
			isChangedOrCancelled = 0
			isCancelled = False
			isChanged = False

			# If the first item in the top section doesn't contain 'til',
			# it must be either cancelled or changed

			if not "til" in topSection[0]:
				isChangedOrCancelled = 1

				# If it says 'Aflyst!'
				if "Aflyst!" in topSection[0]:
					# It must be cancelled
					isCancelled = True
				else:
					# Otherwise it must be changed
					isChanged = True

			if not timeGroups is None:
				startTime = datetime.fromtimestamp(mktime(time.strptime("%s %s %s %s %s" % (timeGroups.group("start_hour"),timeGroups.group("start_minute"), dayOfWeek , timeWeek, year),"%H %M %w %W %Y")))
				endTime = datetime.fromtimestamp(mktime(time.strptime("%s %s %s %s %s" % (timeGroups.group("end_hour"),timeGroups.group("end_minute"), dayOfWeek , timeWeek, year),"%H %M %w %W %Y")))
			else:
				# Grab the date sections, fx: "15/5-2013 15:30 til 17:00"
				dateSections = topSection[0+isChangedOrCancelled].split(" ")

				# Grab the date, being the first (0) section
				if len(dateSections) == 4:
					startDateSection = dateSections[0]
					endDateSection = dateSections[0]

					startTimeSection = dateSections[1]
					endTimeSection = dateSections[3]
				else:
					startDateSection = dateSections[0]
					endDateSection = dateSections[3]

					startTimeSection = dateSections[1]
					endTimeSection = dateSections[4]

				currentTimezone = timezone("Europe/Copenhagen")

				alternativeDayProg = re.compile(r"(?P<day>[0-9]*)/(?P<month>[0-9]*)-(?P<year>[0-9]*)")
				alternativeStartDayGroups = alternativeDayProg.match(startDateSection.strip())
				alternativeEndDayGroups = alternativeDayProg.match(endDateSection.strip())

				startTime = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(alternativeStartDayGroups.group("day")), functions.zeroPadding(alternativeStartDayGroups.group("month")), alternativeStartDayGroups.group("year"), startTimeSection.strip()), "%d/%m-%Y %H:%M")
				endTime = datetime.strptime("%s/%s-%s %s" % (functions.zeroPadding(alternativeEndDayGroups.group("day")), functions.zeroPadding(alternativeEndDayGroups.group("month")), alternativeEndDayGroups.group("year"), endTimeSection.strip()), "%d/%m-%Y %H:%M")

			roomText = ""
			try:
				if not "rer:" in topSection[3 + isChangedOrCancelled]:
					room = topSection[3 + isChangedOrCancelled].strip("Lokale: ").encode('utf-8').replace("r: ","")
			except IndexError:
				pass

			if sameDay(startTime, dayOfWeek, timeWeek, year):
				if type == "private":
					timeElements.append({
						"text" : unicode(timetableElement.text),
						"activity_id" : groups.group("activity_id"),
						"startTime" : startTime,
						"endTime" : endTime,
						"type" : type,
						"school_id" : groups.group("school_id")
					})
				elif type == "outgoing_censor":
					timeElements.append({
						"text" : unicode(timetableElement.text),
						"outbound_censor_id" : groups.group("outbound_censor_id"),
						"startTime" : startTime,
						"endTime" : endTime,
						"type" : type,
						"school_id" : groups.group("school_id")
					})
				elif type == "exam":
					timeElements.append({
						"text" : unicode(timetableElement.text),
						"test_team_id" : groups.group("test_team_id"),
						"startTime" : startTime,
						"endTime" : endTime,
						"type" : type,
						"school_id" : groups.group("school_id")
					})
				elif type == "school":
					# Add to the list
					timeElements.append({
						"text" : unicode(timetableElement.text),
						"activity_id" : groups.group("activity_id"),
						"status" : "changed" if "s2changed" in div["class"] else "cancelled" if "s2cancelled" in div["class"] else "normal",
						"teachers" : teachers,
						"teams" : teams,
						"startTime" : startTime,
						"endTime" : endTime,
						"type" : type,
						"location_text" : unicode(div.text),
						"room_text" : unicode(roomText),
						"school_id" : groups.group("school_id")
					})

	return {
		"status" : "ok",
		"timetable" : timeElements,
		"information" : generalInformation,
		"module_info" : moduleInfo,
		"headers" : headers,
		"term" : {
			"value" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
			"years_string" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
		}
	}

timetable({
	"school_id" : 517,
	"branch_id" : "4733693427",
}, "https://www.lectio.dk/lectio/517/SkemaNy.aspx?type=elev&elevid=4789793691&week=2220144", "22", "2014")