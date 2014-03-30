from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
from datetime import *
import re
import database
import proxy
import functions
import authenticate

def assignments( config ):
	session = authenticate.authenticate(config)

	if session == False:
		return {"status" : "error", "type" : "authenticate"}
	else:
		url = urls.assigment_list.replace("{{SCHOOL_ID}}", str(config["school_id"])).replace("{{STUDENT_ID}}", str(config["student_id"]))

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

		validationRequest = response = proxy.session.get(url, headers=headers)

		html = response.text

		soup = Soup(html)

		firstViewState = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})

		firstEventValidationText = soup.find(id="aspnetForm").find(id="__EVENTVALIDATION")["value"]

		firstEventValidation = urllib.urlencode({"__EVENTVALIDATION" : firstEventValidationText})

		firstResponse = proxy.session.post(url, data='__EVENTTARGET=s%24m%24Content%24Content%24CurrentExerciseFilterCB&__EVENTARGUMENT=&__LASTFOCUS='+firstEventValidation+"&"+firstViewState+"&time=0&__EVENTARGUMENT=&__VIEWSTATE=", headers=headers)

		html = firstResponse.text

		soup = Soup(html)

		viewState = urllib.urlencode({"__VIEWSTATEX" : soup.find(id="__VIEWSTATEX")["value"]})

		eventValidationText = soup.find(id="aspnetForm").find(id="__EVENTVALIDATION")["value"]

		eventValidation = urllib.urlencode({"__EVENTVALIDATION" : eventValidationText})

		response = proxy.session.post(url, data='__EVENTTARGET=s%24m%24Content%24Content%24ShowThisTermOnlyCB&__EVENTARGUMENT=&__LASTFOCUS='+eventValidation+"&"+viewState+"&time=0&__EVENTARGUMENT=&__VIEWSTATE=", headers=headers)

		html = response.text

		soup = Soup(html)

		if soup.find("table", attrs={"id" : "s_m_Content_Content_ExerciseGV"}) is None:
			return {
				"status" : False,
				"error" : "Data not found"
			}

		# Extract table cells
		tableRows = soup.find("table", attrs={"id" : "s_m_Content_Content_ExerciseGV"}).findAll("tr")

		# Remove the header cell
		del tableRows[0]

		assignmentsList = []

		for row in tableRows:
			cells = row.findAll("td")

			s = re.search('([0-9]*)\/([0-9]*)-([0-9]*) ([0-9]*):([0-9]*)',cells[3].text)
			date = functions.zeroPadding(s.group(1)) + "/" + functions.zeroPadding(s.group(2)) + "-" + s.group(3) + " " + s.group(4) + ":" + s.group(5)
			object = {}
			try:
				object["week"] = cells[0].find("span").text
			except BaseException:
				object["week"] = ""
			try:
				object["group"] = unicode(cells[1].find("span").text)
			except BaseException:
				object["group"] = ""
			try:
				object["title"] = unicode(cells[2].find("a").text)
			except BaseException:
				object["title"] = ""
			try:
				object["context_card_id"] = cells[1].find("span")["lectiocontextcard"]
				object["team_id"] = cells[1].find("span")["lectiocontextcard"].replace("HE", "")
			except BaseException:
				object["context_card_id"] = ""
				object["team_id"] = ""
			try:
				prog = re.compile(r"\/lectio\/(?P<school_id>.*)\/ElevAflevering.aspx\?elevid=(?P<student_id>.*)&exerciseid=(?P<exercise_id>.*)&(?P<the_other>.*)")
				urlGroups = prog.match(cells[2].find("a")["href"])
				object["exercise_id"] = urlGroups.group("exercise_id")
			except BaseException:
				object["exercise_id"] = ""
			try:
				object["link"] = cells[2].find("a")["href"]
			except BaseException:
				object["link"] = ""
			try:
				object["date"] = datetime.strptime(date,"%d/%m-%Y %H:%S")
			except BaseException:
				object["date"] = datetime.strptime("1/1-1977 00:01","%d/%m-%Y %H:%S")
			try:
				object["hours"] = float(cells[4].find("span").text.replace(",", ".").strip())
			except BaseException:
				object["hours"] = ""
			try:
				status = unicode(cells[5].find("span").text)
				object["status"] = "handed" if status == "Afleveret" else "missing" if status == "Mangler" else "waiting"
			except BaseException:
				object["status"] = ""
			try:
				object["leave"] = int(cells[6].text.replace(",", ".").replace("%", "").strip())
			except BaseException:
				object["leave"] = ""
			try:
				waiting_for = unicode(cells[7].find("span").text)
				object["waiting_for"] = "student" if waiting_for == "Elev" else "teacher"
			except BaseException:
				object["waiting_for"] = ""
			try:
				object["note"] = unicode(cells[8].text)
			except BaseException:
				object["note"] = ""
			try:
				object["grade"] = unicode(cells[9].text)
			except BaseException:
				object["grade"] = ""
			try:
				object["student_note"] = unicode(cells[10].text)
			except BaseException:
				object["student_note"] = ""

			assignmentsList.append(object)

		return {
			"list" : assignmentsList,
			"status" : "ok",
			"term" : {
            	"value" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0]["value"],
            	"years_string" : soup.find("select", attrs={"id" : "s_m_ChooseTerm_term"}).select('option[selected="selected"]')[0].text
        	}
		}