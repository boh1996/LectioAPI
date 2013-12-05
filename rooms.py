#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import requests
from datetime import *
import functions

def rooms(config):
    roomsList = []

    url = urls.rooms.replace("{{SCHOOL_ID}}", config["school_id"]).replace("{{BRANCH_ID}}", config["branch_id"])

    # Sorting settings
    settings = {
        "__EVENTTARGET" : "m$Content$AktuelAndAfdelingCB$ShowOnlyAktulleCB",
        "m%24ChooseTerm%24term" : str(datetime.strftime(datetime.now(), "%Y")),
    }

    # Insert User-agent headers and the cookie information
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Host" : "www.lectio.dk",
        "Origin" : "https://www.lectio.dk"
    }

    response = requests.post(url, data=settings, headers=headers)

    html = response.text

    soup = Soup(html)

    roomRows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

    for number, name in functions.grouped(roomRows, 2):
        roomsList.append({
            "name" : unicode(name.text),
            "number" : unicode(number.text),
            "room_id" : number["href"].replace("/lectio/%s/SkemaNy.aspx?type=lokale&nosubnav=1&id=" % (config["school_id"]), ""),
            "school_id" : config["school_id"],
            "brand_id" : config["branch_id"]
        })

    return {
        "status" : "ok",
        "rooms" : roomsList
    }