#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import urls
import re
import proxy
from datetime import *
import time
from time import mktime
import functions
import authenticate

def exams ( config ):
	url = "https://www.lectio.dk/lectio/%s/proevehold.aspx?type=elev&studentid=%s" % ( str(config["school_id"], str(config["student_id"])) )