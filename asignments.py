import config
from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
import requests
from datetime import *
import re
import models
import database
import functions
import requests
from sqlalchemy.exc import IntegrityError
import authenticate

def assignments():
    session = authenticate.authenticate(config)

    if session == False:
        print "Error"
    else:
        url = urls.assigment_list.replace("{{SCHOOL_ID}}", config.school_id).replace("{{STUDENT_ID}}", config.lectio_id)

        # Insert the session information from the auth function
        cookies = {
            "lecmobile" : "0",
            "ASP.NET_SessionId" : session["ASP.NET_SessionId"],
            "LastLoginUserName" : session["LastLoginUserName"],
            "lectiogsc" : session["lectiogsc"],
            "LectioTicket" : session["LectioTicket"]
        }

        # Sorting settings
        settings = {
            "s$m$Content$Content$ShowHoldElementDD" : "", # Lectio Team ID
            "s$m$ChooseTerm$term": "", #Year - Eg 2013
            "s$m$Content$Content$ShowThisTermOnlyCB" : "", #on or ""
            "s$m$Content$Content$CurrentExerciseFilterCB" : "", # on or "
        }

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

        # Extract table cells
        tableRows = soup.find("table", attrs={"id" : "s_m_Content_Content_ExerciseGV"}).findAll("tr")

        # Remove the header cell
        del tableRows[0]

        assignmentsList = []

        for row in tableRows:
            cells = row.findAll("td")

            s = re.search('([0-9]*)\/([0-9]*)-([0-9]*) ([0-9]*):([0-9]*)',cells[3].text)
            date = functions.zeroPadding(s.group(1)) + "/" + functions.zeroPadding(s.group(2)) + "-" + s.group(3) + " " + s.group(4) + ":" + s.group(5)
            object = {}
            try:
                object["week"] = cells[0].find("span").text
            except BaseException:
                object["week"] = ""
            try:
                object["group"] = cells[1].find("span").text
            except BaseException:
                object["group"] = ""
            try:
                object["title"] = cells[2].find("a").text
            except BaseException:
                object["title"] = ""
            try:
                object["link"] = cells[2].find("a")["href"]
            except BaseException:
                object["link"] = ""
            try:
                object["date"] = datetime.strptime(date,"%d/%m-%Y %H:%S")
            except BaseException:
                object["date"] = datetime.strptime("1/1-1977 00:01","%d/%m-%Y %H:%S")
            try:
                object["hours"] = cells[4].find("span").text
            except BaseException:
                object["hours"] = ""
            try:
                object["status"] = cells[5].find("span").text
            except BaseException:
                object["status"] = ""
            try:
                object["leave"] = cells[6].text
            except BaseException:
                object["leave"] = ""
            try:
                object["waiting_for"] = cells[7].find("span").text
            except BaseException:
                object["waiting_for"] = ""
            try:
                object["note"] = cells[8].text
            except BaseException:
                object["note"] = ""
            try:
                object["grade"] = cells[9].text
            except BaseException:
                object["grade"] = ""
            try:
                object["student_note"] = cells[10].text
            except BaseException:
                object["student_note"] = ""

            assignmentsList.append(object)

        return assignmentsList