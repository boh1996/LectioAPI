#!/usr/bin/python
# -*- coding: utf8 -*-

import re
import proxy
import functions
import json

def load_list ( config, year, type ):
	if type == "bchold" or type == "bcteacher" or type == "bcstudent" or type == "bcgroup" or type == "bchold":
		year = "y" + str(year)

	remove = "var _localcache_autocomplete_%s_%s_%s = " % ( str(type), str(config["branch_id"]), str(year) )

	url = "https://www.lectio.dk/lectio/%s/cache/DropDown.aspx?type=%s&afdeling=%s&subcache=%s" % ( str(config["school_id"]), str(type), str(config["branch_id"]), str(year) )

	cookies = {}

	# Insert User-agent headers and the cookie information
	headers = {
		"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
		"Content-Type" : "application/x-www-form-urlencoded",
		"Host" : "www.lectio.dk",
		"Origin" : "https://www.lectio.dk",
		"Cookie" : functions.implode(cookies, "{{index}}={{value}}", "; ")
	}

	response = proxy.session.get(url, headers=headers)

	rows = json.loads(response.text.replace(remove, "").strip().replace(";" , ""))

	teams = []
	team_elements = []
	groups = []
	persons = []

	termProg = re.compile(r"(?P<value>.*)\/(?P<end_year>.*)")
	teamNameProg = re.compile(r"(?P<name>.*) \((?P<value>.*)\/(?P<end_year>.*)\)")
	teacherNameProg = re.compile(r"(?P<name>.*) \((?P<abbrevation>.*)\)")
	studentNameProg = re.compile(r"(?P<name>.*) \((?P<class_code>.*)\)")

	for row in rows:
		context_card_id = row[1]

		if "H" in context_card_id:
			teamNameGroups = teamNameProg.match(row[0])

			teams.append({
				"context_cards" : [context_card_id],
				"team_id" : context_card_id.replace("H", "")
			})

			team_elements.append({
				"team_id" : context_card_id.replace("H", ""),
				"term" : {
					"value" : teamNameGroups.group("value") if not teamNameGroups is None else ""
				},
				"name" : teamNameGroups.group("name").encode("utf8") if not teamNameGroups is None else "",
				"active" : True if not row[2] == "i" else False
			})

		elif "G" in context_card_id:
			teams.append({
				"context_cards" : [context_card_id, context_card_id.replace("G", "H")],
				"team_id" : context_card_id.replace("G", "")
			})

			data = {
				"name" : row[0].encode("utf8"),
				"term" : {
					"value" : str(year).replace("y", "")
				},
				"active" : True if not row[2] == "i" else False
			}

			if len(row) > 4:
				data["group_type"] = "built_in" if row[4] == "groupbuiltin" else "own_group"

			groups.append(data)
		elif "T" in context_card_id:
			teacherGroups = teacherNameProg.match(row[0])

			persons.append({
				"name" : teacherGroups.group("name") if not teacherGroups is None else "",
				"abbrevation" : teacherGroups.group("abbrevation") if not teacherGroups is None else "",
				"teacher_id" : context_card_id.replace("T", ""),
				"context_cards" : [context_card_id],
				"active" : True if not row[2] == "i" else False,
				"type" : "teacher"
			})
		elif "S" in context_card_id:
			studentGroups = studentNameProg.match(row[0])

			persons.append({
				"type" : "student",
				"student_id" : context_card_id.replace("S", ""),
				"active" : True if not row[2] == "i" else False,
				"name" : studentGroups.group("name").encode("utf8") if not studentGroups is None else "",
				"class_text" : studentGroups.group("class_code") if not studentGroups is None else "",
				"context_cards" : [context_card_id]
			})


	return {
		"status" : "ok",
		"persons" : persons,
		"teams" : teams,
		"team_elements" : team_elements,
		"groups" : groups
	}

# https://www.lectio.dk/lectio/517/cache/DropDown.aspx?type=favorites&afdeling=4733693427&dt=%2bsvQVm%2fjhkz0rp3DufIc9g%3d%3d4789793695