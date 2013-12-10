#!/usr/bin/python
# -*- coding: utf8 -*-

'''dates_2letters = {
    "ma" : 1,
    "ti" : 2,
    "on" : 3,
    "to" : 4,
    "fr" : 5,
    unicode("lø") : 6,
    unicode("sø") : 7
}

dates_full = {
    "mandag" : 1,
    "tirsdag" : 2,
    "onsdag" : 3,
    "torsdag" : 4,
    "fredag" : 5,
    unicode("lørdag") : 6,
    unicode("søndag"): 7,
}'''

activity_short_date_regex = r"([a-z]*) ([0-9]*/[0-9]*) ([0-9]*)\. modul, uge ([0-9]*)"
name_with_abbrevation_regex = r"(?P<name>.*) \((?P<abbrevation>.*)\)"
room_name_regex = r"(?P<room_number>.*) - (?P<room_name>.*)"
student_name_from_list = r"(?P<name>.*), (?P<class>.*)"
document_info = r"(?P<name>.*), (?P<file_size>.*)"
activity_updated_regex = r": (?P<created_date>[0-9]*)/(?P<created_month>[0-9]*)-(?P<created_year>[0-9]*) (?P<created_hour>[0-9]*):(?P<created_minute>[0-9]*) af (?P<created_teacher>.*) Sidst rettet: (?P<updated_date>[0-9]*)/(?P<updated_month>[0-9]*)-(?P<updated_year>[0-9]*) (?P<updated_hour>[0-9]*):(?P<updated_minute>[0-9]*) af (?P<updated_teacher>.*)"
activity_homework_regexs = [
    {"name" : "book", "expression" : r"(?P<class>.*) (?P<subject>.*): (?P<writers>.*): ?(?P<name>.*), (?P<publisher>.*), ?(?P<pages>[0-9]*-[0-9]*) \(kernestof\)\s(?P<note>.*)"},
    {"name" : "note", "expression" : "(?P<note>.*)"}
]
teacher_url_regex = r"\/lectio\/(?P<school_id>[0-9]*)\/SkemaNy.aspx\?type=laerer&laererid=(?P<teacher_id>[0-9]*)"
room_url_regex = r"\/lectio\/(?P<school_id>[0-9]*)/SkemaNy.aspx\?type=lokale&nosubnav=1&id=(?P<room_id>[0-9]*)&week=(.*)"
team_class_name_regex = r"(?P<class_name>.*) (?P<team_name>.*)"
team_url_regex = r"\/lectio\/(?P<school_id>[0-9]*)\/SkemaNy.aspx\?type=holdelement&holdelementid=(?P<team_id>[0-9]*)&week=(.*)"
class_url_regex = r"\/lectio\/(?P<school_id>[0-9]*)\/SkemaNy.aspx\?type=stamklasse&klasseid=(?P<class_id>[0-9]*)&week=(.*)"
student_url_regex = r"\/lectio\/(?P<school_id>[0-9]*)\/SkemaNy.aspx\?type=elev&elevid=(?P<student_id>[0-9]*)&week=(.*)"
document_url_regex = r"\/lectio\/(?P<school_id>[0-9]*)/dokumenthent.aspx\?doctype=absensedocument&documentid=(?P<document_id>[0-9]*)"
file_size_regex = r", (?P<size>.*) (?P<unit_name>.*)"