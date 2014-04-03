import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import timetable as timetableApi
from url_creator import *

def importPublicTimetable ( schools_id, branch_id, type, element_id ):