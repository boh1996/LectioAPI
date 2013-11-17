import config
from bs4 import BeautifulSoup as Soup
import urllib
import urls
import re
import models
import database
from sqlalchemy.exc import IntegrityError

f = urllib.urlopen(urls.schools_list)
html = f.read()

soup = Soup(html)

school_tags = soup.find(id="schoolsdiv").find_all(attrs={"class":"buttonHeader"})

schools = []

for school in school_tags:
    name = school.find("a").text.encode('ascii', 'ignore').replace("X - ", "").replace(" - ","").replace("Z - ", "")
    ids = re.search('/lectio/([0-9]*)/default.aspx\?lecafdeling=([0-9]*)',school.find("a")["href"])
    SchoolObject = models.School(name,ids.group(1),ids.group(2))
    schools.append(SchoolObject)
    database.session.add(SchoolObject)

database.session.commit();

