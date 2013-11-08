import urllib
import requests
from bs4 import BeautifulSoup as Soup
import urls

def authenticate (config):
    url = urls.login_url.replace("{{SCHOOL_ID}}", config.school_id).replace("{{BRANCH_ID}}", config.branch_id)

    # Retrieve the base information, to retrieve ViewState
    base = requests.get(url)
    soup = Soup(base.text)

    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Referer" : url,
        "Host" : "www.lectio.dk",
        "Origin" : "https://www.lectio.dk",
    }

    # Insert validation information
    eventValidationTest = soup.find(id="aspnetForm").find(id="__EVENTVALIDATION")["value"]

    eventValidation = urllib.urlencode({"__EVENTVALIDATION" : eventValidationTest})
    response = requests.post(url, data="m%24Content%24username2="+config.username.strip()+"&m%24Content%24password2="+config.password.strip()+"&time=0&__EVENTARGUMENT=&__VIEWSTATE=&"+eventValidation+"&__EVENTTARGET=m%24Content%24submitbtn2&__VIEWSTATEX="+soup.find(id="__VIEWSTATEX")["value"], headers=headers, allow_redirects=False)

    if "LastLoginUserName" in response.cookies:
        return response.cookies
    else:
        return False