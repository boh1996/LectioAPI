#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy

def schools():
    session = proxy.session

    schoolList = []

    response = session.get(urls.schools_list)
    html = response.text

    soup = Soup(html)

    if soup.find(id="schoolsdiv") is None:
        return {
            "status" : False,
            "error" : "Data not found"
        }

    school_tags = soup.find(id="schoolsdiv").find_all(attrs={"class":"buttonHeader"})

    for school in school_tags:
        name = unicode(school.find("a").text).replace("X - ", "").replace(" - ","").replace("Z - ", "")
        ids = re.search('/lectio/([0-9]*)/default.aspx\?lecafdeling=([0-9]*)', school.find("a")["href"])
        schoolList.append({
            "name" : unicode(name),
            "school_id" : ids.group(1),
            "branch_id" : ids.group(2)
        })

    return {
        "status" : "ok",
        "schools" :schoolList
    }