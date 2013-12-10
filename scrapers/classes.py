#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
import requests
import re
from datetime import *

def classes(config):
    url = urls.student_classes.replace("{{SCHOOL_ID}}", config["school_id"]).replace("{{BRANCH_ID}}", config["branch_id"])

    classList = []

    # Sorting settings
    settings = {
        "m%24ChooseTerm%24term" : str(datetime.strftime(datetime.now(), "%Y")),
        "__EVENTTARGET:" : "m$Content$AktuelAndAfdelingCB$ShowOnlyAktulleCB"
    }

    # Insert User-agent headers and the cookie information
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Host" : "www.lectio.dk",
        "Origin" : "https://www.lectio.dk"
    }

    response = requests.post(url, data={}, headers=headers)

    html = response.text

    soup = Soup(html)

    classListObjects = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

    for classElement in classListObjects:
        classList.append({
            "name" : classElement.text,
            "class_id" : classElement["href"].replace("/lectio/%s/SkemaNy.aspx?type=stamklasse&klasseid=" % (config["school_id"]), ""),
            "school_id" : config["school_id"],
            "branch_id" : config["branch_id"]
        })

    return {
        "status" : "ok",
        "classes" : classList,
        "year" : str(datetime.strftime(datetime.now(), "%Y"))
    }