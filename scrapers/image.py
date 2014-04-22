from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
from datetime import *
import re
import database
import proxy
import functions
import authenticate

def image ( config, picture_id ):
	session = authenticate.authenticate(config)
	if session == False:
		return { "status" : "error", "type" : "authenticate" }
	else:
		url = "https://www.lectio.dk/lectio/%s/GetImage.aspx?pictureid=%s&fullsize=1" % ( str(config["school_id"]), str(picture_id) )

		# Insert the session information from the auth function
		cookies = {
			"lecmobile" : "0",
			"ASP.NET_SessionId" : session["ASP.NET_SessionId"],
			"LastLoginUserName" : session["LastLoginUserName"],
			"lectiogsc" : session["lectiogsc"],
			"LectioTicket" : session["LectioTicket"]
		}

		# Insert User-agent headers and the cookie information
		headers = {
			"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
			"Content-Type" : "application/x-www-form-urlencoded",
			"Host" : "www.lectio.dk",
			"Origin" : "https://www.lectio.dk",
			"Cookie" : functions.implode(cookies, "{{index}}={{value}}", "; ")
		}

		response = proxy.session.get(url, headers=headers)

		return response.text