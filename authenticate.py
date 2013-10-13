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
    eventValidation = urllib.urlencode({"__EVENTVALIDATION" : "7BY2j4lely4ahWOpscccBOPS5wvMRZRL6o+oRDvtegQobPOXPgvj7pLXiMQPBGIxGdLpySs/0XQnfeBMI/kbyno5uBSlX7txoVGBhKfjqpgdjHmSez24vsY8shOlAhPhpXSwekUDJ0Boc8kRnZcht0xZBrfbSHiV1j4Yv/I9V1wUzNUX7YvWU3FNbXzoI2p+VupeTLPhwbvMpK0guGI46I8sHREt8zBW6ktlFvAk+Dm2RIq61f7FmWIDvo3DEjqTgIKktXU07gC0fgQribl0rI02Q9WoaCKGNljL0BY/9jdlX5BwWMIN+K4cSDkfrrs1q004M6AqNHL1Wd/O9wB/ow=="})
    response = requests.post(url, data="m%24Content%24username2="+config.username+"&m%24Content%24password2="+config.password+"&time=0&__EVENTARGUMENT=&__VIEWSTATE=&"+eventValidation+"&__EVENTTARGET=m%24Content%24submitbtn2&__VIEWSTATEX="+soup.find(id="__VIEWSTATEX")["value"], headers=headers, allow_redirects=False)

    if "LastLoginUserName" in response.cookies:
        return response.cookies
    else:
        return False