import config
from bs4 import BeautifulSoup as Soup
import urllib
import urls
import re

def schools():
    schoolList = []

    f = urllib.urlopen(urls.schools_list)
    html = f.read()

    soup = Soup(html)

    school_tags = soup.find(id="schoolsdiv").find_all(attrs={"class":"buttonHeader"})

    for school in school_tags:
        name = unicode(school.find("a").text).replace("X - ", "").replace(" - ","").replace("Z - ", "")
        ids = re.search('/lectio/([0-9]*)/default.aspx\?lecafdeling=([0-9]*)',school.find("a")["href"])
        schoolList.append({
            "name" : name,
            "school_id" : ids.group(1),
            "branch_id" : ids.group(2)
        })

    return {
        "status" : "ok",
        "schools" :schoolList
    }