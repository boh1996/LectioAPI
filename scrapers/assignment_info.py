#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import requests
from datetime import *
import time
from time import mktime
import values
import codecs
import functions

def assignment_info(config, session, assignment_id):
    url = urls.assignment_info.replace("{{SCHOOL_ID}}", str(config.school_id)).replace("{{ASSIGNMENT_ID}}", str(assignment_id)).replace("{{STUDENT_ID}}",str(config["lectio_id"]))

    # Insert the session information from the auth function
    cookies = {
        "lecmobile" : "0",
        "ASP.NET_SessionId" : session["ASP.NET_SessionId"],
        "LastLoginUserName" : session["LastLoginUserName"],
        "lectiogsc" : session["lectiogsc"],
        "LectioTicket" : session["LectioTicket"]
    }

    settings = {}

    # Insert User-agent headers and the cookie information
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Host" : "www.lectio.dk",
        "Origin" : "https://www.lectio.dk",
        "Cookie" : functions.implode(cookies, "{{index}}={{value}}", "; ")
    }

    response = requests.post(url, data=settings, headers=headers)

    html = response.text

    soup = Soup(html)