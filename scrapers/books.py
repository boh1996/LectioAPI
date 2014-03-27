from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
import requests
from datetime import *
import re
import models
import functions
from time import mktime
import requests
import authenticate
import calendar
from datetime import *

def books(config):
    session = authenticate.authenticate(config)

    if session == False:
        return {"status" : "error", "type" : "authenticate"}
    else:
        url = urls.books_list.replace("{{SCHOOL_ID}}", str(config.school_id)).replace("{{STUDENT_ID}}", str(config.lectio_id)).replace("{{BRANCH_ID}}", str(config.branch_id))

        # Insert the session information from the auth function
        cookies = {
            "lecmobile" : "0",
            "ASP.NET_SessionId" : session["ASP.NET_SessionId"],
            "LastLoginUserName" : session["LastLoginUserName"],
            "lectiogsc" : session["lectiogsc"],
            "LectioTicket" : session["LectioTicket"]
        }

        # Sorting settings
        settings = {
            "time" : "0",
            "__EVENTTARGET" : "s$m$Content$Content$ShowActiveOnlyCB",
            "__EVENTARGUMENT:" : "",
            "__VIEWSTATEX" : "kwUAAGlpZQk2Mjc5NjMyNjBpbARrAG1rAWcBbAJoaWlsBmsCfQGbc34dAQAAAGsDZwFrBGUaRWxldmVuIEJvIEhhbnMgVGhvbXNlbiwgMnFkbAJoaWRsAmcCaWwCawVlA29mZmwEZwJpZGwCZxVpZGwCZwFpbAJrBnFkZwNpZGwCZwFpZGwCZwVpZGwCZwFpZGwCZwNpbAJrB3BsBmhpZGwMZwFpZGwCZwFpbAJrCG1kZwNpbARrCG1rBnBkZwVpaWwCawZxZGwIZwFpbAJrCG1kZwNpbAJrCWwAZGcFaXMRaWwCawpxZGpsAGwAbABkZGRkZGRkZGRkcwBkZGRkZGcHaXMRaWwGawtxawpwawxoZGpsAGwAbABkZGRkZGRkZGRkcwBkZGRkbAJoaWlsBGsNZQlsaXN0IG1heFdrDmcCZGRnB2lkbAJnAWlsBGsIbWsGcGRnCWlpbAJrBnBkbAJnA2lzEWlsBGsKcWsGcGRqbABsAGwAZGRkZGRkZGRkZHMAZGRkZGRnC2lpbARrD2RrBnBkZGcBaWRsAmcBaWRsBGcBaWwCawhtZGcFaXMRaWwCawpxZGpsAGwAbABkZGRkZGRkZGRkcwBkZGRkZGcCaWRsAmcBaWRsCmcBaWpkZGwBZwFkZwNpamRkbAFoZGcFaWRsAmcDaXMRaWwCawpxZGpsAGwAbABkZGRkZGRkZGRkcwBkZGRkZGcHaWRsAmcDaXMRaWwCawpxZGpsAGwAbABkZGRkZGRkZGRkcwBkZGRkZGcJaWRsAmcDaXMRaWwCawpxZGpsAGwAbABkZGRkZGRkZGRkcwBkZGRkZHIKZRxzJG0kQ29udGVudCRDb250ZW50JG15cHVic0dWaXMMZGRkZGRkbgFlB0R1bW15SURkZ/////8PZGRkZGUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fbAFlJHMkbSRDb250ZW50JENvbnRlbnQkU2hvd0FjdGl2ZU9ubHlDQmUgcyRtJENvbnRlbnQkQ29udGVudCRCZEJvb2tMb2FuR1ZpcwxkZGRkZGRuAWUHRHVtbXlJRHMKcwF7NCcBAQAAAABzAXsvJwEBAAAAAHMBezYnAQEAAAAAcwF7OCcBAQAAAABzAXswJwEBAAAAAHMBezEnAQEAAAAAcwF7MicBAQAAAABzAXszJwEBAAAAAHMBezUnAQEAAAAAcwF7NycBAQAAAABnAWRkZGRlNXMkbSRDb250ZW50JENvbnRlbnQkcHVibGlzaGVyU2FsZXNDdHJsJHRvdGFsU2FsZXNHcmlkaXMMZGRkZGRkbgFlB0R1bW15SURkZ/////8PZGRkZGUccyRtJENvbnRlbnQkQ29udGVudCR0YWJzdHJpcGlpZGhkZSJzJG0kQ29udGVudCRDb250ZW50JHJlc2VydmF0aW9uc0dWaXMMZGRkZGRkbgFlB0R1bW15SURkZ/////8PZGRkZGUxcyRtJENvbnRlbnQkQ29udGVudCRwdWJsaXNoZXJTYWxlc0N0cmwkc2Nob29sR3JpZGlzDGRkZGRkZG4BZQdEdW1teUlEZGf/////D2RkZGRlKHMkbSRDb250ZW50JENvbnRlbnQkZWJvb2tzRm9yRmF2b3JpdGhvbGRpcwxkZGRkZGRuAWUHRHVtbXlJRGRn/////w9kZGRkZS9zJG0kQ29udGVudCRDb250ZW50JHB1Ymxpc2hlclNhbGVzQ3RybCRib29rR3JpZGlzDGRkZGRkZG4BZQdEdW1teUlEZGf/////D2RkZGRlL3MkbSRDb250ZW50JENvbnRlbnQkZWJvb2tzRm9yRmF2b3JpdEhvbGRTdHVkZW50aXMMZGRkZGRkbgFlB0R1bW15SURkaGRkZGQQAAAABXVzcmlkE1ZhbGlkYXRlUmVxdWVzdE1vZGUIbGVjdGlvaWQFbXR5cGUKRW50aXR5TmFtZQxhdXRvY29tcGxldGUHVmlzaWJsZQtzaG93aGVhZGVycxFOYXZpZ2F0ZVVybExlY3RpbwtDdXJyZW50RGF0YRRfUmVxdWlyZXNEYXRhQmluZGluZwtfIURhdGFCb3VuZAtfIUl0ZW1Db3VudAhDc3NDbGFzcwRfIVNCCVRlYWNoZXJJZAEAAQAAAP////8BAAAAAAAAAAQBAAAAf1N5c3RlbS5Db2xsZWN0aW9ucy5HZW5lcmljLkxpc3RgMVtbU3lzdGVtLk9iamVjdCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XV0DAAAABl9pdGVtcwVfc2l6ZQhfdmVyc2lvbgUAAAgICQIAAAAGAAAABgAAABACAAAACAAAAAkDAAAACQQAAAAJBQAAAAkGAAAACQcAAAAJCAAAAA0CDAkAAABKTWFjb20uTGVjdGlvLkNvbW1vbiwgVmVyc2lvbj0xLjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPW51bGwFAwAAABJNYWNvbS5MZWN0aW8uVXNySUQBAAAABl92YWx1ZQAJCQAAAJ9zfh0BAAAADAoAAABDTWFjb20uTGVjdGlvLCBWZXJzaW9uPTEuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49bnVsbAUEAAAAGU1hY29tLkxlY3Rpby5MZWN0aW9SZWZVcmwBAAAABGRhdGEEKk1hY29tLkxlY3Rpby5MZWN0aW9SZWZVcmwrTGVjdGlvUmVmVXJsRGF0YQoAAAAKAAAACQsAAAABBQAAAAQAAAAJDAAAAAEGAAAABAAAAAkNAAAAAQcAAAAEAAAACQ4AAAABCAAAAAQAAAAJDwAAAAULAAAAKk1hY29tLkxlY3Rpby5MZWN0aW9SZWZVcmwrTGVjdGlvUmVmVXJsRGF0YQQAAAAGcmVmdXJsEHJlZnVybFVybEVuY29kZWQSX2lzU3RhdGljUmVmZXJlbmNlCkZvcmNlSFRUUFMBAQAAAQEKAAAABhAAAABjRWJvZy9EZWZhdWx0LmFzcHg/cHJldnVybD1CRCUyZlVzZXJSZXNlcnZhdGlvbnMuYXNweCUzZkVsZXZJRCUzZDQ3ODk3OTM2OTElMjZwcmV2dXJsJTNkZm9yc2lkZS5hc3B4CgAAAQwAAAALAAAABhEAAABfQkQvQm9va3MuYXNweD9wcmV2dXJsPUJEJTJmVXNlclJlc2VydmF0aW9ucy5hc3B4JTNmRWxldklEJTNkNDc4OTc5MzY5MSUyNnByZXZ1cmwlM2Rmb3JzaWRlLmFzcHgKAAABDQAAAAsAAAAGEgAAAGdFYm9nL0NyZWF0ZUVib29rLmFzcHg/cHJldnVybD1CRCUyZlVzZXJSZXNlcnZhdGlvbnMuYXNweCUzZkVsZXZJRCUzZDQ3ODk3OTM2OTElMjZwcmV2dXJsJTNkZm9yc2lkZS5hc3B4CgAAAQ4AAAALAAAABhMAAAB/QkQvU3R1ZGVudFJlc2VydmF0aW9ucy5hc3B4P0VsZXZJRD00Nzg5NzkzNjkxJnByZXZ1cmw9QkQlMmZVc2VyUmVzZXJ2YXRpb25zLmFzcHglM2ZFbGV2SUQlM2Q0Nzg5NzkzNjkxJTI2cHJldnVybCUzZGZvcnNpZGUuYXNweAoAAAEPAAAACwAAAAYUAAAAZ0Vib2cvQ3JlYXRlRWJvb2suYXNweD9wcmV2dXJsPUJEJTJmVXNlclJlc2VydmF0aW9ucy5hc3B4JTNmRWxldklEJTNkNDc4OTc5MzY5MSUyNnByZXZ1cmwlM2Rmb3JzaWRlLmFzcHgKAAAL/HO0KMmthSVEyM2CYSzxt4utYL4=",
            "__VIEWSTATE:" : "",
            "__EVENTVALIDATION" : "6OqghX6xZOeeKUKrRIw7ICUy+1VPS7casHOeKUMsfDj6sV1LAjCrokugRNNSYnB3AtE4D/xEDXGXEUMRV8fCTtH6dqeuxRYS3AAMtYA04et59bwlJNT3c0QGpPiKz05X2fng07YiA1EvrNnE7J2D0smysbBQFSyR2nfIDZ8f6eWBxsh2hXpJJp7aM7qydcWFGsMBDBO3OCBWoLKpI/4bHnW/GiUzfgOYqQ8qCIe91qkwdY2JO1s/Szu1CkSeWJPjohv4N2UiRhGyxtJDEXUAho/DmOUtCRMrJliE7WJBf6rGpwELcczgLirEbiGyhY9b2HAkUorn0H6Kc6FL/iHvAZNQqalZQJDp0RK0QCi/6Qzo1rrCU/sVzkB7S4zDO23hyoLFmOkwm6ILTN3hehLMVOgvq9TJqhcxUFHb47KrVEI2l94BmOGnWH1eiQlr24I35qsepc7/nNp5UvL5GX/MHg==",
            "__LASTFOCUS:" : "",
            "__VIEWSTATEENCRYPTED:" : "",
            "LectioPostbackId:" : "",
            "s$m$searchinputfield:" : ""
        }

        # Insert User-agent headers and the cookie information
        headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Host" : "www.lectio.dk",
            "Origin" : "https://www.lectio.dk",
            "Cookie" : functions.implode(cookies, "{{index}}={{value}}", "; ")
        }

        response = requests.post(url, data=settings, headers=headers)

        html = response.text

        soup = Soup(html)

        loans = soup.find("table", attrs={"id" : "s_m_Content_Content_BdBookLoanGV"}).findAll("tr")
        loansList = []

        for loan in loans:
            columns = loan.findAll("td")
            if len(columns) > 0:
                # Define the short team pattern "2q KE" etc..
                shortTeamPreg = re.compile(r"(?P<class>\w.) (?P<team>\w.)")

                # Define the long team pattern "2012 FY/i" etc...
                yearTeamPreg = re.compile(r"(?P<year>[0-9]*) (?P<team>[0-9A-Z]*)\/(?P<class>\w*)")

                # Find and prepare the team string text
                teamText = columns[1].text.replace("\n", "").replace("\t", "").strip()
                teamRows = None
                preg = ""

                # Check which and if any pattern matches the string
                if shortTeamPreg.match(teamText):
                    preg = "short"
                    teamRows = shortTeamPreg.match(teamText)
                elif yearTeamPreg.match(teamText):
                    preg = "long"
                    teamRows = yearTeamPreg.match(teamText)

                delivery_reg_date = columns[3].text.replace("\n","").strip()
                if not delivery_reg_date == "":
                    delivery_reg_date = str(mktime(datetime.strptime(delivery_reg_date, "%d-%m-%Y").utctimetuple()))[:-2]

                loansList.append({
                    "title" : columns[0].text.replace("\n", "").replace("\t", "").strip().encode("utf8"),
                    "team" : teamRows.group("team").encode("utf8") if not teamRows == None else  "",
                    "year" : teamRows.group("year").encode("utf8") if not teamRows == None and preg == "long" else  "",
                    "class" : teamRows.group("class").encode("utf8") if not teamRows == None else "",
                    "lending_reg_date" : str(mktime(datetime.strptime(columns[2].text.replace("\n","").strip(), "%d-%m-%Y").utctimetuple()))[:-2],
                    "delivery_reg_date" : delivery_reg_date,
                    "delivery_date" : str(mktime(datetime.strptime(columns[4].text.replace("\n","").strip(), "%d-%m-%Y").utctimetuple()))[:-2],
                    "price" : columns[5].text.replace("\n", "").replace("\t", "").replace(",", ".").strip()
                })

        return {
            "status" : "ok",
            "loans" : loansList
        }
