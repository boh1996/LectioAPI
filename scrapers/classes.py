#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import proxy
import re
from datetime import *
import urllib

def classes( config, term = False ):
    url = urls.student_classes.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{BRANCH_ID}}", str(config["branch_id"]))

    classList = []

    response = proxy.session.get(url)

    html = response.text

    soup = Soup(html)

    if not term == False:
        term = "&m%24ChooseTerm%24term=" + term
    else:
        term = ""

    firstViewState = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})

    eventValidationText = soup.find(id="aspnetForm").find(id="__EVENTVALIDATION")["value"]

    eventValidation = urllib.urlencode({"__EVENTVALIDATION" : eventValidationText})

    response = proxy.session.post(url, data="__EVENTTARGET=" + "m%24Content%24AktuelAndAfdelingCB%24ShowOnlyAktulleCB"+ firstViewState + "&" + eventValidation + term)

    html = response.text

    soup = Soup(html)

    if soup.find(attrs={"id" : "m_Content_AktuelAndAfdelingCB_ShowOnlyCurrentShoolAfdelingCB"}):

        firstViewState = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})

        eventValidationText = soup.find(id="aspnetForm").find(id="__EVENTVALIDATION")["value"]

        eventValidation = urllib.urlencode({"__EVENTVALIDATION" : eventValidationText})

        response = proxy.session.post(url, data="__EVENTTARGET=" + "m%24Content%24AktuelAndAfdelingCB%24ShowOnlyCurrentShoolAfdelingCB" + "&m%24Content%24AktuelAndAfdelingCB%24ShowOnlyCurrentShoolAfdelingCB=on&" + firstViewState + term + "&" + eventValidation )

        html = response.text

        soup = Soup(html)

    if soup.find(attrs={"id" : "m_Content_contenttbl"}) is None:
        return {
            "status" : False,
            "error" : "Data not found"
        }

    classListObjects = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

    for classElement in classListObjects:
        prog = re.compile(r"\/lectio\/(?P<school_id>[0-9]*)\/SkemaNy.aspx\?type=(?P<type_name>.*)&klasseid=(?P<class_id>[0-9]*)")
        groups = prog.match(classElement["href"])
        type = groups.group("type_name").encode("utf8") if not groups is None else ""
        classList.append({
            "name" : classElement.text.encode("utf8"),
            "class_id" : groups.group("class_id").encode("utf8") if not groups is None else "",
            "type" : "base_class" if type == "stamklasse" else type,
            "school_id" : str(config["school_id"]),
            "branch_id" : str(config["branch_id"])
        })

    return {
        "status" : "ok",
        "classes" : classList,
        "term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
    }