import urllib
import proxy
from bs4 import BeautifulSoup as Soup
import urls
import functions

def authenticate ( config ):
    url = urls.login_url.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{BRANCH_ID}}", str(config["branch_id"]))

    # Retrieve the base information, to retrieve ViewState
    base = proxy.session.get(url)
    soup = Soup(base.text)

    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Referer" : url,
        "Host" : "www.lectio.dk",
        "Origin" : "https://www.lectio.dk",
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    # Insert validation information
    eventValidationTest = soup.find(id="aspnetForm").find(id="__EVENTVALIDATION")["value"]

    eventValidation = urllib.urlencode({"__EVENTVALIDATION" : eventValidationTest})

    viewS = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})

    eventV = eventValidation

    response = proxy.session.post(url, data="m%24Content%24username2="+config["username"].strip()+"&m%24Content%24password2="+config["password"].strip()+"&time=0&__EVENTARGUMENT=&__VIEWSTATE=&"+eventV+"&__EVENTTARGET=m%24Content%24submitbtn2&"+viewS,headers=headers, allow_redirects=False)

    if "LastLoginUserName" in response.cookies:
        return response.cookies
    else:
        return False