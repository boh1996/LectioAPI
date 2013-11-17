from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
import requests
from datetime import *
import re
import models
import functions
import requests
import authenticate

def userinfo(config):
    session = authenticate.authenticate(config)

    if session == False:
        return {"status" : "error", "type" : "authenticate"}
    else:
        url = urls.front_page_url.replace("{{SCHOOL_ID}}", config.school_id)

        # Insert the session information from the auth function
        cookies = {
            "lecmobile" : "0",
            "ASP.NET_SessionId" : session["ASP.NET_SessionId"],
            "LastLoginUserName" : session["LastLoginUserName"],
            "lectiogsc" : session["lectiogsc"],
            "LectioTicket" : session["LectioTicket"]
        }

        # Insert User-agent headers and the cookie information
        headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Host" : "www.lectio.dk",
            "Origin" : "https://www.lectio.dk",
            "Cookie" : functions.implode(cookies, "{{index}}={{value}}", "; ")
        }

        response = requests.post(url, headers=headers)

        html = response.text

        soup = Soup(html)

        lectio_user_id = soup.find("div", attrs={"id" : "s_m_masterleftDiv"}).find("a")["href"]
        picture_id = soup.find("img", attrs={"id" : "s_m_HeaderContent_picctrlthumbimage"})["src"]
        teamRows = soup.find("div", attrs={"id" : "s_m_Content_Content_HoldAndGroupList"}).find("table").findAll("tr")

        teams = []
        buildInGroups = []
        ownGroups = []

        # Teams
        for row in teamRows[0].findAll("td")[1].findAll("a"):
            id = row["href"].replace("/lectio/517/SkemaNy.aspx?type=holdelement&holdelementid=","")
            name = row.text
            teams.append({
                "id" : id,
                "name" : name
            })

        # Build in Groups
        for row in teamRows[1].findAll("td")[1].findAll("a"):
            id = row["href"].replace("/lectio/517/SkemaNy.aspx?type=holdelement&holdelementid=","")
            name = row.text
            buildInGroups.append({
                "id" : id,
                "name" : name
            })

        # Own groups
        for row in teamRows[2].findAll("td")[1].findAll("a"):
            id = row["href"].replace("/lectio/517/SkemaNy.aspx?type=holdelement&holdelementid=","")
            name = row.text
            ownGroups.append({
                "id" : id,
                "name" : name
            })

        # Student name
        name = re.sub(r'"Eleven (\w+), (\w+) - Forside"',r'\2',soup.find("div", attrs={"id" : "s_m_HeaderContent_MainTitle"}).text)

        # Info
        informations = []
        schoolTable = soup.find("table", attrs={"id" : "s_m_Content_Content_importantInfo"})
        infoObjects = schoolTable.findAll("tr")

        if not infoObjects is None:
            for info in infoObjects:
                infoType = ""
                tds = info.findAll("td")
                if  tds[0].find("img")["src"] == "/lectio/img/prio1.auto" :
                    infoType = "red"
                elif tds[0].find("img")["src"] == "/lectio/img/prio2.auto":
                    infoType = "yellow"
                elif tds[0].find("img")["src"] == "/lectio/img/prio3.auto":
                    infoType = "grey"
                informations.append({
                    "text" : tds[1].find("span").text,
                    "type" : infoType
                })

        return {
            "status" : "ok",
            "lectio_user_id" : lectio_user_id.replace("/lectio/517/SkemaNy.aspx?type=elev&elevid=", ""),
            "lectio_picture_id" : picture_id.replace("/lectio/517/GetImage.aspx?pictureid=", ""),
            "teams" : teams,
            "buildInGroups" : buildInGroups,
            "ownGroups" : ownGroups,
            "name" : name,
            "information" : informations
        }