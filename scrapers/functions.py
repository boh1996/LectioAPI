#!/usr/bin/python
# -*- coding: utf8 -*-
from itertools import izip
import re

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