import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import subject_list as subjectListApi

def importSubjectList ( school_id, start, end ):
	try:

		objectList = subjectListApi.subject_list(start, end, school_id)

		for row in objectList:
			unique = {
				"subject_id" : row["subject_id"]
			}

			notice_ids = []

			element = {
				"subject_id" : row["subject_id"],
				"name" : row["name"],
				"abbrevation" : row["abbrevation"]
			}

			status = sync.sync(db.subjects, unique, element)

		return True

	except Exception, e:
		error.log(__file__, False, str(e))
		return False

#importSubjectList(517, 500, 540)
#importSubjectList(517, 540, 580)
#importSubjectList(517, 580, 615)
#importSubjectList(517, 1363322359, 1363322359)
#importSubjectList(517, 1364002147, 1364002147)
#importSubjectList(517, 1452164869, 1452164869)