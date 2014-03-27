#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import functions

def ressources(config):
    ressourceList = []

    url = urls.ressources.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{BRANCH_ID}}", str(config["branch_id"]))

    # Sorting settings
    settings = {
        "__EVENTTARGET" : "m$Content$AktuelAndAfdelingCB$ShowOnlyAktulleCB",
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

    ressourceRows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

    idProg = re.compile(r"\/lectio\/(?P<school_id>.*)\/SkemaNy.aspx\?type=(?P<type_name>.*)&nosubnav=1&id=(?P<ressource_id>.*)")

    for name, title in functions.grouped(ressourceRows, 2):
        idGroups = idProg.match(name["href"])
        ressourceList.append({
            "name" : unicode(name.text),
            "ressource_id" : idGroups.group("ressource_id") if not idGroups is None else "",
            "title" : unicode(title.text),
            "school_id" : config["school_id"],
            "branch_id" : config["branch_id"],
            "type" : idGroups.group("type_name").encode("utf-8") if not idGroups is None else ""
        })

    return {
        "status" : "ok",
        "ressources" : ressourceList,
        "term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
    }

