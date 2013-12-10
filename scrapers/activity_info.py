#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import requests
from datetime import *
import time
from time import mktime
import values
import codecs
import functions

def activity_info(config, session, activity_id):
    url = urls.activity_info.replace("{{SCHOOL_ID}}", config.school_id).replace("{{ACTIVITY_ID}}", activity_id)

    # Insert the session information from the auth function
    cookies = {
        "lecmobile" : "0",
        "ASP.NET_SessionId" : session["ASP.NET_SessionId"],
        "LastLoginUserName" : session["LastLoginUserName"],
        "lectiogsc" : session["lectiogsc"],
        "LectioTicket" : session["LectioTicket"]
    }

    settings = {}

    # Insert User-agent headers and the cookie information
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Host" : "www.lectio.dk",
        "Origin" : "https://www.lectio.dk",
        "Cookie" : functions.implode(cookies, "{{index}}={{value}}", "; ")
    }

    response = requests.post(url, data=settings, headers=headers)

    html = response.text

    soup = Soup(html)

    # Find all the different rows in the table
    rows = soup.find("div", attrs={"id" : "m_Content_LectioDetailIslandLesson_pa"}).find("table").findAll("td")
    headers = soup.find("div", attrs={"id" : "m_Content_LectioDetailIslandLesson_pa"}).find("table").findAll("th")

    # Make rows[n] match headers[n]
    for index, element in enumerate(rows):
        table = element.find_parent("table")
        if table["class"][0] == u"NoFrame":
            del rows[index]

    # Generate a map of rows
    rowMap = functions.mapRows(headers, rows)

    # Retrieve the values
    showed_in_values = unicode(rowMap["Vises"].text).split(", ")
    showed_in = []

    type = unicode(rowMap["Type"].text)
    status = unicode(rowMap["Status"].text)
    students_resserved = unicode(rowMap["Deltagerereserveret"].text)

    teams = [] # Done
    students = [] # Done
    ressources = [] # Missing
    rooms = [] # Done
    teachers = [] # Done
    documents = [] # Done
    links = [] # Done
    students_education_assigned = [] # Missing
    homework = []

    # Created and updated dates
    metaProg = re.compile(values.activity_updated_regex)

    metaElements = rowMap["Systeminformation"].text.strip().split("\n")
    metaString = ""
    for me in metaElements:
        metaString = metaString + " " + me.replace("\t\t\t\t", "").replace("\r", "").strip()

    metaGroups = metaProg.search(metaString)

    # Loop through the documents and append to the list
    documentTable = rowMap["Dokumenter"].find("table")
    if not documentTable == None:
        documentRows = documentTable.findAll("td")
        for documentRow in documentRows:
            # Split the size from the unit
            fileSizeProg = re.compile(values.file_size_regex)
            fileSizeGroups = fileSizeProg.search(documentRow.text)

            # Find the different document info elements
            elements = documentRow.findAll("a")

            # Filter the id from the document url
            documentProg = re.compile(values.document_url_regex)
            documentGroups = documentProg.search(elements[1]["href"])

            # Append to the list
            documents.append({
                "name" : unicode(elements[1].text),
                "size" : {
                    "size" : fileSizeGroups.group("size").replace(",", "."),
                    "unit" : fileSizeGroups.group("unit_name")
                },
                "document_id" : documentGroups.group("document_id")
            })

    # Loop through the students and append to the list
    studentRows = rowMap["Elever2"].findAll("a")
    for student,classObject in functions.grouped(studentRows,2):
        # Filter the id from the class URL
        studentClassProg = re.compile(values.class_url_regex)
        studentClassGroups = studentClassProg.search(classObject["href"])

        # Filter the student id from the URL
        studentIdProg = re.compile(values.student_url_regex)
        studentIdGroups = studentIdProg.search(student["href"])

        students.append({
            "name" : unicode(student.text),
            "class" : unicode(classObject.text),
            "context_card_id" : student["lectiocontextcard"],
            "student_id" : studentIdGroups.group("student_id"),
            "class_id" : studentClassGroups.group("class_id")
        })

    # Loop through the teams and append to the list
    for team in rowMap["Hold"].findAll("a"):
        # Filter the class name from the team name
        teamNameProg = re.compile(values.team_class_name_regex)
        teamNameGroups = teamNameProg.search(unicode(team.text))

        # Filter the id from the URL
        teamIdProg = re.compile(values.team_url_regex)
        teamIdGroups = teamIdProg.search(team["href"])

        if not teamIdGroups == None:
            # Append to the list
            teams.append({
                "class" : teamNameGroups.group("class_name"),
                "team" : teamNameGroups.group("team_name"),
                "team_id" : teamIdGroups.group("team_id")
            })

    # Loop through the values and append English and Computer easy readable values
    for value in showed_in_values:
        if value == u"i dags- og ugeændringer":
            showed_in.append("day_and_week_changes")
        elif value == u"Inde i berørte skemaer":
            showed_in.append("timetable")
        elif value == u"I toppen af berørte skemaer":
            showed_in.append("top_of_timetable")

    # Loop through the links and append them to the list
    for link in rowMap["Links"].findAll("a"):
        links.append({
            "url" : link["href"],
            "title" : unicode(link.text)
        })

    # Loop through the rooms and append them to the list
    for room in rowMap["Lokaler"].findAll("a"):
        # Initialize variables
        roomName = ""
        roomNumber = ""

        # Filter the number from the name
        roomNameProg = re.compile(values.room_name_regex)
        roomNameGroups = roomNameProg.search(unicode(room.text))

        if not roomNameGroups == None:
            roomName = roomNameGroups.group("room_name")
            roomNumber = roomNameGroups.group("room_number")

         # Initialize roomId RegEx
        roomIdProg = re.compile(values.room_url_regex)

        # Filter the id from the URL
        roomIdGroups = roomIdProg.search(room["href"])

        # Append the room to the list
        rooms.append({
            "name" : roomName,
            "number" : roomNumber,
            "room_id" : roomIdGroups.group("room_id")
        })

    # Loop through the teachers and append them to the list
    for teacher in rowMap["Laerere"].findAll("a"):
        # Filter the abbrevation from the name
        teacherNameProg = re.compile(values.name_with_abbrevation_regex)
        teacherNameGroups = teacherNameProg.search(unicode(teacher.text))

        # Filter the id from the URL
        teacherIdProg = re.compile(values.teacher_url_regex)
        teacherIdGroups = teacherIdProg.search(teacher["href"])

        # Append to the list
        teachers.append({
            "context_card_id" : teacher["lectiocontextcard"],
            "name" : teacherNameGroups.group("name"),
            "abbrevation" : teacherNameGroups.group("abbrevation"),
            "teacher_id" : teacherIdGroups.group("teacher_id"),
            "school_id" : teacherIdGroups.group("school_id")
        })

    # Loop over the diferent homework notes and append to the list
    for object in values.activity_homework_regexs:
        prog = re.compile(object["expression"])
        matches = prog.finditer(unicode(rowMap["Lektier"].text))

        # Loop over the matches
        for element in matches:
            if object["name"] == "note":
                if not element.group("note") == "":
                    homework.append({
                        "note" : element.group("note"),
                        "type" : "note"
                    })
            else:
                homework.append({
                    "note" : element.group("note"),
                    "class" : element.group("class"),
                    "authors" : element.group("writers").split(", "),
                    "name" : element.group("name"),
                    "pages" : element.group("pages"),
                    "subject" : element.group("subject"),
                    "publisher" : element.group("publisher"),
                    "type" : "book"
            })
    # Initialize note variable
    note = unicode(rowMap["Note"].text)

    # Return all the information
    return {
        "status" : "ok",
        "time" : unicode(rowMap["Tidspunkt"].text),
        "teams" : teams,
        "type" : "school" if type == "Lektion" else "other_activity" if type == "Anden aktivitet" else "other",
        "students_education_assigned" : students_education_assigned,
        "teachers" : teachers,
        "rooms" : rooms,
        "ressources" : ressources,
        "note" : note,
        "documents" : documents,
        "homework" : homework, # Match books with the list of books
        "links" : links,
        "students_resserved" : "true" if students_resserved.strip() == "Ja" else "false",
        "showed_at" : showed_in,
        "status" : "done" if status == "Afholdt" else "planned" if status == "Planlagt" else "canceled" if status == "Aflyst" else "other",
        "students" : students,
        "created" : {
            "at" : datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(metaGroups.group("created_date")),functions.zeroPadding(metaGroups.group("created_month")),functions.zeroPadding(metaGroups.group("created_year")),functions.zeroPadding(metaGroups.group("created_hour")),functions.zeroPadding(metaGroups.group("created_minute"))), "%d/%m-%Y %H:%M"),
            "by" : metaGroups.group("created_teacher")
        },
        "updated" : {
            "at" : datetime.strptime("%s/%s-%s %s:%s" % (functions.zeroPadding(metaGroups.group("updated_date")),functions.zeroPadding(metaGroups.group("updated_month")),functions.zeroPadding(metaGroups.group("updated_year")),functions.zeroPadding(metaGroups.group("updated_hour")),functions.zeroPadding(metaGroups.group("updated_minute"))), "%d/%m-%Y %H:%M"),
            "by" : metaGroups.group("updated_teacher")
        },
        "term" : {
            "value" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            "years_string" : soup.find("select", attrs={"id" : "m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        }
    }