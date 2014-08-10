#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
import re
import proxy
from datetime import *

def students(config, term = False, letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Z", "Æ", "Ø", "Å", "?"]):
    studentList = []

    if not term == False:
        term = "&m%24ChooseTerm%24term=" + term
    else:
        term = ""

    url = urls.students.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{FIRST_LETTER}}", "A").replace("{{BRANCH_ID}}", str(config["branch_id"]))

    response = proxy.session.get(url)

    html = response.text

    soup = Soup(html)

    firstViewState = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})

    eventValidationText = soup.find(id="aspnetForm").find(id="__EVENTVALIDATION")["value"]

    eventValidation = urllib.urlencode({"__EVENTVALIDATION" : eventValidationText})

    response = proxy.session.post(url, data="__EVENTTARGET=" + "m%24Content%24AktuelAndAfdelingCB%24ShowOnlyAktulleCB&m%24Content%24AktuelAndAfdelingCB%24ShowOnlyCurrentShoolAfdelingCB=on&"+ firstViewState + "&" + eventValidation)

    html = response.text

    soup = Soup(html)

    if not soup.find(id="__VIEWSTATEX") is None:
        firstViewState = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})
    else:
        response = proxy.session.post(url, data="__EVENTTARGET=" + "m%24Content%24AktuelAndAfdelingCB%24ShowOnlyAktulleCB&"+ firstViewState + "&" + eventValidation)

        html = response.text

        soup = Soup(html)

    # Loop through all the letters
    for letter in letters:
        url = urls.students.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{FIRST_LETTER}}", letter).replace("{{BRANCH_ID}}", str(config["branch_id"]))

        # Sorting settings
        settings = {
            "m%24ChooseTerm%24term" : str(datetime.strftime(datetime.now(), "%Y")),
        }

        # Insert User-agent headers and the cookie information
        headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Host" : "www.lectio.dk",
            "Origin" : "https://www.lectio.dk"
        }

        if not soup.find(id="__VIEWSTATEX") is None:
            response = proxy.session.post(url, data=firstViewState + term)
        else:
            if len(term) > 1:
                response = proxy.session.post(url, data=term.replace("&", ""))
            else:
                response = proxy.session.get(url)

        html = response.text

        soup = Soup(html)

        if soup.find("table", attrs={"id" : "m_Content_contenttbl"}) is None:
            return {
                "status" : False,
                "error" : "Data not found"
            }

        studentRows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

        for student in studentRows:
            # Define the different name patters
            patterns = [
                r"(?P<name>.*) \((?P<class>.*) (?P<class_student_id>.*)\)",
                r"(?P<name>.*) \((?P<class>.*), (?P<year>.*) (?P<class_description>.*), (?P<status>.*)\)",
                r"(?P<name>.*) \((?P<organization>.*), (?P<class>.*), (?P<status>.*)\)",
                 r"(?P<name>.*) \((?P<organization>.*), (?P<type>.*), (?P<class>.*), (?P<status>.*)\)",
                r"(?P<name>.*) \((?P<class_number>.*) (?P<class>.*) (?P<class_student_id>[0-9]*)\)"
            ]

            # Check if the patterns matches
            for pattern in patterns:
                prog = re.compile(pattern)
                if prog.match(student.text):
                    studentInformation = prog.match(student.text)

            # Get the matched regex groups
            groups = studentInformation.groupdict()

            if "class" in groups:
                if "class_number" in groups:
                    studentClass = "%s %s" % (studentInformation.group("class_number"), studentInformation.group("class"))
                else:
                    studentClass = studentInformation.group("class")
            else:
                studentClass = ""

            urlProg = re.compile(r"\/lectio\/(?P<school_id>[0-9].*)\/SkemaNy.aspx\?type=(?P<type_name>.*)&elevid=(?P<student_id>.*)")
            urlGroups = urlProg.match(student["href"])

            # Append the student information
            studentList.append({
                "context_card_id" : student["lectiocontextcard"],
                "student_id" : urlGroups.group("student_id") if not urlGroups is None and "student_id" in urlGroups.groupdict() else "",
                "name" : studentInformation.group("name").encode("utf8") if not groups is None and "name" in groups else "",
                "class_name" : studentClass,
                "class_student_id" : studentInformation.group("class_student_id") if not groups is None and "class_student_id" in groups else "",
                "class_description" : studentInformation.group("class_description") if not groups is None and "class_description"in groups else "",
                "status" : studentInformation.group("status").encode("utf8") if not groups is None and "status" in groups else "active",
                "school_id" : config["school_id"],
                "branch_id" : config["branch_id"],
                "type" : urlGroups.group("type_name").encode("utf8") if not urlGroups is None and "type_name" in groups else ""
            })

    print len(studentList)

    return {
        "status" : "ok",
        "students" : studentList,
        "term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
    }