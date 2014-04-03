def timetable_url ( element_type, school_id, branch_id, element_id ):
	if element_type == "teacher":
		return "https://www.lectio.dk/lectio/%s/SkemaNy.aspx?type=laerer&laererid=%s" % ( str(school_id), str(element_id) )
	elif element_type == "student":
		return "https://www.lectio.dk/lectio/%s/SkemaNy.aspx?type=elev&elevid=%s" % ( str(school_id), str(element_id) )
	elif element_type == "ressource" or element_type == "room":
		return "https://www.lectio.dk/lectio/%s/SkemaNy.aspx?type=lokale&nosubnav=1&id=%s" % ( str(school_id), str(element_id) )
	elif element_type == "class":
		return "https://www.lectio.dk/lectio/%s/SkemaNy.aspx?type=stamklasse&klasseid=%s" % ( str(school_id), str(element_id) )
	elif element_type == "team_element" or element_type == "group":
		return "https://www.lectio.dk/lectio/%s/SkemaNy.aspx?type=holdelement&holdelementid=%s" % ( str(school_id), str(element_id) )