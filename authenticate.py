import config
import cookielib, urllib2, urllib
from bs4 import BeautifulSoup as Soup
import urls
from cookielib import Cookie

def authenticate ():
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    url = urls.login_url.replace("{{SCHOOL_ID}}", config.school_id).replace("{{BRANCH_ID}}", config.branch_id)

    base = opener.open(url)
    soup = Soup(base, "lxml")

    '''CookieContainer = Cookie()
    CookieContainer["isloggedin3"] = "N"

    for cookie in cj:
        if cookie.name == "NET_SessionId":
            CookieContainer["ASP.NET_SessionId"] = cookie.value
        elif cookie.name == "lectiogsc":
            CookieContainer["lectiogsc"] = cookie.value

    for cookie in CookieContainer:
        cj.set_cookie(cookie)'''

    settings = {
        "m$Content$username2" : config.username,
        "m$Content$password2": config.password,
        "time" : 0,
        "__EVENTARGUMENT:" : "",
        "__VIEWSTATE" : "",
        "__EVENTVALIDATION" : soup.find(id="__EVENTVALIDATION")["value"],
        "__EVENTTARGET" : "m$Content$submitbtn2",
        "__VIEWSTATEX" : "8QAAAGlpZQstMTUxMzYxNjIxMWlsBGsAZwFrAWcBbAJoaWRsAmcCaWwCawJlA29mZmwCZwNpZGwCZwFpZGwCZwVpZGwCZwVpZGwEaGlkbAJnA2lkbAZnAWlsAmsDZTVIVFggU3Vra2VydG9wcGVuIC0gSyYjMjQ4O2Jlbmhhdm5zIFRla25pc2tlIEd5bW5hc2l1bWRnBWlkbAJnAWlkbAJoaWwCawRlAjUwZGcHaWRsAmcBaWRsAmhpamlsAmsFcGRkZGRnAWlkbAJnA2lpbAJrBmcyZGRyAWURbSRDb250ZW50JExvZ2luTVZpaWRoZAcAAAAJTG9naW5WaWV3E1ZhbGlkYXRlUmVxdWVzdE1vZGUMYXV0b2NvbXBsZXRlCWlubmVyaHRtbAltYXhsZW5ndGgHQ2hlY2tlZAlNYXhMZW5ndGgAdKSEw0sxHwMhiTNR9mghwx8Ymk8",
    }

    f = opener.open(url, urllib.urlencode(settings))
    print f.geturl()


authenticate()