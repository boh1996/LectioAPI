import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import timetable as timetableApi
from url_creator import *
import outgoing_censor
import exam_team
import activity_info

def importPublicTimetable ( school_id, branch_id, type, element_id, number_of_weeks = 1 ):
