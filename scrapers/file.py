#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import re
import proxy
from datetime import *
import time
from time import mktime
import values
import codecs
import functions
import authenticate
import os.path
import context_card

# https://www.lectio.dk/lectio/517/dokumenthent.aspx?documentid=9274230873 - Document
# https://www.lectio.dk/lectio/517/dokumenthent.aspx?doctype=messagedoc&documentid=9249053092 - Message File
# https://www.lectio.dk/lectio/517/ExerciseFileGet.aspx?type=elevopgave&entryid=7543477675 - Exercise file
# https://www.lectio.dk/lectio/517/dokumenthent.aspx?doctype=absensedocument&documentid=9010851242 - Timetable Document
# https://www.lectio.dk/lectio/517/ExerciseFileGet.aspx?type=opgavedef&exercisefileid=7265076020 Excercise description file


def file ( config, session = False ):
	if config"type"] == "document":
		url = "https://www.lectio.dk/lectio/%s/dokumenthent.aspx?documentid=%s" % ( config["school_id"], config["document_id"] )
	elif config["type"] == "message_file":
		url = "https://www.lectio.dk/lectio/%s/dokumenthent.aspx?doctype=messagedoc&documentid=%s" % ( config["school_id"], config["document_id"] )
	elif config["type"] == "exercise_file":
		url = "https://www.lectio.dk/lectio/%s/ExerciseFileGet.aspx?type=elevopgave&entryid=%s" % (config["school_id"], config["exercise_file_id"] )
	elif config["type"] == "timetable_document":
		url = "https://www.lectio.dk/lectio/%s/dokumenthent.aspx?doctype=absensedocument&documentid=%s" % ( config["school_id"], config["timetable_document"] )
	elif config["type"] == "excercise_description_file":
		url = "https://www.lectio.dk/lectio/%s/ExerciseFileGet.aspx?type=opgavedef&exercisefileid=%s" % ( config["school_id"], config["excercise_description_file"] )

	if session is False:
		session = authenticate.authenticate(config)

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

	r = proxy.get(url, stream=True)

	file_name = config["file_name"]

    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()