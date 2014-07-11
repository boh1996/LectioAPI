import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import xprs_subjects as xprsSubjectsApi

def importXPRSSubjects ( school_id, start, end, increase, checkLevels = False, levels = ["01", "02", "03", "04", "05", "06"] ):
	try:

		objectList = xprsSubjectsApi.xprs_subjects(start, end, increase, school_id, checkLevels, levels)

		for row in objectList:
			unique = {
				"xprs_subject_id" : row["xprs_subject_id"]
			}

			notice_ids = []

			for x in row["notices"]:
				status = sync.sync(db.notices, {"name" : x}, {"name" : x})

				notice_ids.append(status["_id"])

			level = row["level"]

			if "-" in row["code"]:
				level = "-"

			element = {
				"xprs_subject_id" : row["xprs_subject_id"],
				"context_card_id" : row["context_card_id"],
				"name" : row["name"],
				"code" : row["code"].replace("-", ""),
				"subject_sub_type" : row["subject_sub_type"],
				"level" : level,
				"code_full" : row["code_full"],
				"notices" : row["notices"],
				"notice_ids" : notice_ids,
				"code_full_name" : row["code_full_name"]
			}

			status = sync.sync(db.xprs_subjects, unique, element)

		return True

	except Exception, e:
		error.log(__file__, False, str(e))
		return False

#importXPRSSubjects(517, 6043, 6048, 1, True, ["01"])
#importXPRSSubjects(517, 7000, 7019, 1, True, ["01", "02"])
#importXPRSSubjects(517, 1453150702, 1453150720, 1, False, False)
#importXPRSSubjects(517, 1453150720, 1453150750, 1, False, False)
#importXPRSSubjects(517, 1453150750, 1453150790, 1, False, False)
#importXPRSSubjects(517, 1453150790, 1453150830, 1, False, False)
#importXPRSSubjects(517, 1453150830, 1453150867, 1, False, False)