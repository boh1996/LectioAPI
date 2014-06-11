#!/usr/bin/python
# -*- coding: utf8 -*-
from itertools import izip
import re
from datetime import datetime
from pytz import timezone

def weeks ( numberOfWeeks = 4 ):
    # Get the datetime for the current moment, with Europe/Copenhagen as a timezone
    currentWeekDateTime = datetime.date(datetime.now(timezone('Europe/Copenhagen')))

    # Get the current week number
    currentWeek = int(currentWeekDateTime.strftime("%U"))+1

    # The currentWeek+numberOfWeeks, it can be larger then the max number of weeks
    endWeek = currentWeek+numberOfWeeks

    # If the year has changed
    yearChange = False

    # The current year
    startYear = int(currentWeekDateTime.strftime("%Y"))

    # Initialize the weeks variable
    weeks = []

    # Get the max number of weeks in the current year
    maxWeeks = int(datetime.strptime(str(startYear) + "-12-31", "%Y-%m-%d").strftime("%U"))

    # Fill content into the 'weeks' list
    for i in range(currentWeek, endWeek):

        # If the current number is larger then the maximum number of weeks, calculate the new week
        if i > maxWeeks:
            weeks.append(currentWeek+numberOfWeeks-i)
        else:
            weeks.append(i)

    # If the year has changed, set the year changed to true
    if currentWeek+numberOfWeeks > maxWeeks:
        yearChange = True

    return {
        "weeks" : weeks,
        "year_changed" : yearChange,
        "start_year" : startYear,
        "current_week" : currentWeek,
        "current_week_datetime" : currentWeekDateTime
    }

def implode (list, pattern, delemiter):
    string = ""
    for index, value in list.iteritems():
        string = string + pattern.replace("{{index}}", index).replace("{{value}}", value) + delemiter

    return string.rstrip(delemiter)

def zeroPadding(string):
    integer = int(string)
    if integer < 10:
        return "0" + str(integer)
    else:
        return str(integer)

def grouped(iterable, n):
    return izip(*[iter(iterable)]*n)

def cleanText ( text ):
    return text.replace("\t", "").replace("\n", "").replace("\r", "").strip()

# Map the rows with appropriate headingnames if headers[n] = rows[n]
def mapRows(headers, rows, seperator = ":"):
    mappings = {}
    headerNumbers = {}

    for index, header in enumerate(headers):
        headerNumber = 1
        headerName = unicode(header.text.replace(seperator, "").strip().replace(" ", "").replace(u"æ","ae").replace(u"å", "aa").replace(u"ø", "oe"))
        if not headerName in headerNumbers:
                headerNumbers[headerName] = headerNumber
        else:
            headerNumber = headerNumbers[headerName]+1
            headerNumbers[headerName] = headerNumbers[headerName]+1

        if headerName in mappings:
            headerName = headerName+str(headerNumber)
        mappings[headerName] = rows[index]

    return mappings

timeProg = re.compile(r"(?P<hour>.*):(?P<minute>)")

# Test if new is larger than old
def timeLarger ( new, old ):
    newTimeGroups = timeProg.match(new)
    oldTimeGroups = timeProg.match(old)
    larger = False

    if newTimeGroups is None or oldTimeGroups is None:
        return False

    if newTimeGroups.group("hour") == oldTimeGroups("hour"):
        if newTimeGroups.group("minute") > oldTimeGroups("minute"):
            return True
        else:
            return False
    elif newTimeGroups.group("hour") > oldTimeGroups("hour"):
        return True
    else:
        return False