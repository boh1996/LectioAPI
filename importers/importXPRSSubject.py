import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import context_card

def importXPRSSubject ( school_id, xprs_subject_id ):
	try:

		objectList = context_card.xprs_subject({
			"school_id" : school_id,
			"context_card_id" : "XF" + str(xprs_subject_id)
		})

		if objectList["status"] == "ok":

			row = objectList["xprs_subject"]

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
		else:
			if "error" in objectList:
				error.log(__file__, False, objectList["error"])
				return False
			else:
				error.log(__file__, False, "Unknown error")
				return False


	except Exception, e:
		error.log(__file__, False, str(e))
		return False