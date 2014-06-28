#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def rooms(config):
    roomsList = []

    url = urls.rooms.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{BRANCH_ID}}", str(config["branch_id"]))

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

    response = proxy.session.post(url, data=settings, headers=headers)

    html = response.text

    soup = Soup(html)

    if soup.find("table", attrs={"id" : "m_Content_contenttbl"}) is None:
        return {
            "status" : False,
            "error" : "Data not found"
        }

    roomRows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

    idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy.aspx\?type=(?P<type_name>.*)&nosubnav=1&id=(?P<room_id>.*)")

    for number, name in functions.grouped(roomRows, 2):
        idGroups = idProg.match(number["href"])
        roomsList.append({
            "name" : unicode(name.text),
            "number" : unicode(number.text),
            "room_id" : idGroups.group("room_id") if "room_id" in idGroups.groupdict() else "",
            "school_id" : config["school_id"],
            "branch_id" : config["branch_id"],
            "type" : "room" if idGroups.group("type_name") == "lokale" and "type_name" in idGroups.groupdict() else ""
        })

    return {
        "status" : "ok",
        "rooms" : roomsList
    }