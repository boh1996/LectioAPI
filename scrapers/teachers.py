#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy

def teachers(config):
    teachersList = []

    url = urls.teachers.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{BRANCH_ID}}", str(config["branch_id"]))

    # Insert User-agent headers and the cookie information
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Host" : "www.lectio.dk",
        "Origin" : "https://www.lectio.dk"
    }

    response = proxy.session.get(url)

    html = response.text

    soup = Soup(html)

    if soup.find("table", attrs={"id" : "m_Content_contenttbl"}) is None:
        return {
            "status" : False,
            "error" : "Data not found"
        }

    # Find the teacher a tags
    teacherRows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

    # Loop through, find the infomation and append
    for teacher in teacherRows:
        # Seperate the name from the initial
        prog = re.compile(r"(?P<name>.*) \((?P<initial>.*)\)")
        nameReg = prog.match(teacher.text)

        idProg = re.compile(r"\/lectio\/(?P<school_id>[0-9]*)/SkemaNy.aspx\?type=(?P<type_name>.*)&laererid=(?P<teacher_id>.*)")
        idGroups = idProg.match(teacher["href"])

        # Append the teacher data to the list
        teachersList.append({
            "name" : nameReg.group("name").encode("utf8") if not nameReg is None else "",
            "initial" : nameReg.group("initial").encode("utf8") if not nameReg is None else "",
            "context_card_id" : teacher["lectiocontextcard"],
            "teacher_id" : idGroups.group("teacher_id") if not idGroups is None else "",
            "type" : idGroups.group("type_name").encode("utf8") if not idGroups is None else "",
            "school_id" : config["school_id"],
            "branch_id" : config["branch_id"]
        })

    # Return status and the list
    return {
        "status" : "ok",
        "teachers" : teachersList,
        "term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
    }