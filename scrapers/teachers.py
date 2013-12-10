#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import requests

def teachers(config):
    teachersList = []

    url = urls.teachers.replace("{{SCHOOL_ID}}", config["school_id"]).replace("{{BRANCH_ID}}", config["branch_id"])

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

    # Find the teacher a tags
    teacherRows = soup.find("table", attr={"id" : "m_Content_contenttbl"}).findAll("a")

    # Loop through, find the infomation and append
    for teacher in teacherRows:
        # Seperate the name from the initial
        prog = re.compile(r"(?P<name>\w*) \(?P<initial>\w*\)")
        nameReg = prog.match(unicode(teacher.text))

        # Append the teacher data to the list
        teachersList.append({
            "name" : nameReg.group("name"),
            "initial" : nameReg.group("initial"),
            "context_card_id" : teacher["lectiocontextcard"],
            "teacher_id" : teacher["href"].replace("/lectio/%s/SkemaNy.aspx?type=laerer&laererid=" % (config["school_id"]), ""),
            "school_id" : config["school_id"],
            "brand_id" : config["branch_id"]
        })

    # Return status and the list
    return {
        "status" : "ok",
        "teachers" : teachersList
    }