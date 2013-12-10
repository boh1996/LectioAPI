#!/usr/bin/python
# -*- coding: utf8 -*-
from itertools import izip

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