import urllib
import requests
from bs4 import BeautifulSoup as Soup
import urls
import functions

def authenticate (config):
    url = urls.login_url.replace("{{SCHOOL_ID}}", config.school_id).replace("{{BRANCH_ID}}", config.branch_id)

    # Retrieve the base information, to retrieve ViewState
    base = requests.get(url)
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

    #viewS = "8AAAAGlpZQotMjMxNTQyMTExaWwEawBnAWsBZwFsAmhpZGwCZwJpbAJrAmUDb2ZmbAJnA2lkbAJnAWlkbAJnBWlkbAJnBWlkbARoaWRsAmcDaWRsBmcBaWwCawNlNUhUWCBTdWtrZXJ0b3BwZW4gLSBLJiMyNDg7YmVuaGF2bnMgVGVrbmlza2UgR3ltbmFzaXVtZGcFaWRsAmcBaWRsAmhpbAJrBGUCNTBkZwdpZGwCZwFpZGwCaGlqaWwCawVwZGRkZGcBaWRsAmcDaWlsAmsGZzJkZHIBZRFtJENvbnRlbnQkTG9naW5NVmlpZGhkBwAAAAlMb2dpblZpZXcTVmFsaWRhdGVSZXF1ZXN0TW9kZQxhdXRvY29tcGxldGUJaW5uZXJodG1sCW1heGxlbmd0aAdDaGVja2VkCU1heExlbmd0aAAj19IUcjRcRxl5n5r%2BQAW3cK1O1g%3D%3D"

    viewS = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})

    #viewS = soup.find(id="__VIEWSTATEX")["value"]

    eventV = eventValidation

    #response = requests.post(url, data="m%24Content%24username2="+config.username.strip()+"&m%24Content%24password2="+config.password.strip()+"&time=0&__EVENTARGUMENT=&__VIEWSTATE=&"+eventValidation+"&__EVENTTARGET=m%24Content%24submitbtn2&__VIEWSTATEX="+soup.find(id="__VIEWSTATEX")["value"],headers=headers, allow_redirects=True)
    response = requests.post(url, data="m%24Content%24username2="+config.username.strip()+"&m%24Content%24password2="+config.password.strip()+"&time=0&__EVENTARGUMENT=&__VIEWSTATE=&"+eventV+"&__EVENTTARGET=m%24Content%24submitbtn2&"+viewS,headers=headers, allow_redirects=False)

    if "LastLoginUserName" in response.cookies:
        return response.cookies
    else:
        return False