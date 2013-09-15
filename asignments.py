import config
from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
import re
import models
import database
from sqlalchemy.exc import IntegrityError
import authenticate

cj = authenticate.authenticate()

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

url = urls.assigment_list.replace("{{SCHOOL_ID}}", config.school_id).replace("{{STUDENT_ID}}", config.lectio_id)
settings = {
    "s$m$Content$Content$ShowHoldElementDD" : "", # Lectio Team ID
    "s$m$ChooseTerm$term": "", #Year - Eg 2013
    "s$m$Content$Content$ShowThisTermOnlyCB" : "", #on or ""
    "s$m$Content$Content$CurrentExerciseFilterCB" : "", # on or "

}
params = urllib.urlencode(settings)
f = urllib2.urlopen(url, params)
response = f.read()

print response