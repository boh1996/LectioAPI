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

def timetable( config, url, week, year, session = False ):
	if session == False:
		cookies = {}
	else:
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

	# Fetch the general information celss
	generalInformationDays = rows[2].findAll("td")
	generalInformation = []

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
					if week == 1:
						timeWeek = 0
					else:
						# Subtract one, because 0 is the first week
						timeWeek = week-1

					dayOfWeek = index-1
					date = time.strptime("%s %s %s" % (dayOfWeek,timeWeek, year),"%w %W %Y")
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
							"message" : content.text,
							"timestamp" : date
						})
					else:
						# Compile the regular expression
						prog = re.compile(r"\/lectio\/(?P<school_id>[0-9]*)\/aktivitet\/aktivitetinfo.aspx\?id=(?P<activity_id>[0-9]*)&(?P<prev_url>.*)")
						activityGroups = prog.match(element["href"])
						generalInformation.append({
							"message" : content.text,
							"activity_id" : activityGroups.group("activity_id"),
							"status" : "changed" if "s2changed" in div["class"] else "cancelled" if "s2cancelled" in div["class"] else "normal",
							"timestamp" : date
						})

	# Find all the day elements
	timeElements = []
	dayElements = rows[3].findAll("td")

	# Loop over the days
	index = 0
	dayOfWeek = 1
	for dayElement in dayElements:
		# Increment the day
		index = index+1

		dayOfWeek = index-1

		# The time module uses "0" as the first week of the year
		if week == 1:
			timeWeek = 0
		else:
			# Subtract one, because 0 is the first week
			timeWeek = week-1

		# Find all the "a" tags, representing timetable elements
		timetableElements = dayElement.findAll("a")

		# Loop over the timetable elements
		for timetableElement in timetableElements:

			#The type of the event, "private" or "school"
			type = None

			# Locate the different types of information in the url, and find the different RegEx groups
			expressions = [
				{"type" : "private", "expression" : r"\/lectio\/(?P<school_id>[0-9]*)\/privat_aftale.aspx\?aftaleid=(?P<activity_id>[0-9]*)"},
				{"type" : "school",  "expression" : r"\/lectio\/(?P<school_id>[0-9]*)\/aktivitet\/aktivitetinfo.aspx\?id=(?P<activity_id>[0-9]*)&(?P<prev_url>.*)"},
			]

			# Loop over the expressions
			groups = []
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
				"room_text" : unicode(roomText)
			})

	return {
		"status" : "ok",
		"timetable" : timeElements,
		"information" : generalInformation,
		"term" : {
			"value" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
			"years_string" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
		}
	}