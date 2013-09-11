import config
from bs4 import BeautifulSoup as Soup
import urllib
import urls

f = urllib.urlopen(urls.schools_list)
html = f.read()

soup = Soup(html, "lxml")

school_tags = soup.find(id="schoolsdiv").find_all(attrs={"class":"buttonHeader"})

for school in school_tags:
    print school.find("a").text.encode('ascii', 'ignore')