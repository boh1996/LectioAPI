#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import proxy
import re
from datetime import *

def classes( config ):
    url = urls.student_classes.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{BRANCH_ID}}", str(config["branch_id"]))

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

    response = proxy.session.get(url, headers=headers)

    html = response.text

    soup = Soup(html)

    classListObjects = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

    for classElement in classListObjects:
        prog = re.compile(r"\/lectio\/(?P<school_id>[0-9]*)\/SkemaNy.aspx\?type=(?P<type_name>.*)&klasseid=(?P<class_id>[0-9]*)")
        groups = prog.match(classElement["href"])
        classList.append({
            "name" : classElement.text.encode("utf8"),
            "class_id" : groups.group("class_id").encode("utf8") if not groups is None else "",
            "type" : groups.group("type_name").encode("utf8") if not groups is None else "",
            "school_id" : config["school_id"],
            "branch_id" : config["branch_id"]
        })

    return {
        "status" : "ok",
        "classes" : classList,
        "year" : str(datetime.strftime(datetime.now(), "%Y")),
        "term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
    }