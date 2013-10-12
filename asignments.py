import config
from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
import re
import models
import database
import functions
import requests
from sqlalchemy.exc import IntegrityError
import authenticate

session = authenticate.authenticate()

if session == False:
    print "Error"
else:
    url = urls.assigment_list.replace("{{SCHOOL_ID}}", config.school_id).replace("{{STUDENT_ID}}", config.lectio_id)

    cookies = {
        "lecmobile" : "0",
        "ASP.NET_SessionId" : session["ASP.NET_SessionId"],
        "LastLoginUserName" : session["LastLoginUserName"],
        "lectiogsc" : session["lectiogsc"],
        "LectioTicket" : session["LectioTicket"]
    }

    settings = {
        "s$m$Content$Content$ShowHoldElementDD" : "", # Lectio Team ID
        "s$m$ChooseTerm$term": "", #Year - Eg 2013
        "s$m$Content$Content$ShowThisTermOnlyCB" : "", #on or ""
        "s$m$Content$Content$CurrentExerciseFilterCB" : "", # on or "
    }

    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Host" : "www.lectio.dk",
        "Origin" : "https://www.lectio.dk",
        "Cookie" : functions.implode(cookies, "{{index}}={{value}}", "; ")
    }

    response = requests.post(url, data=settings, headers=headers)

    html = response.text

    print html