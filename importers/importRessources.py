import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from datetime import datetime
from database import *
import error
import sync
import ressources as ressourcesApi

def importRessources ( school_id, branch_id ):
	try:
		objectList = ressourcesApi.ressources({
			"school_id" : school_id,
			"branch_id" : branch_id
		})

		if objectList is None:
			error.log(__file__, False, "Unknown Object")
			return False

		if not "status" in objectList:
			error.log(__file__, False, "Unknown Object")
			return False

		if objectList["status"] == "ok":
			for row in objectList["ressources"]:
				unique = {
					"ressource_id" : str(row["ressource_id"])
				}

				terms = []

				existsing = db.persons.find(unique).limit(1)

				if existsing.count() > 0:
					existsing = existsing[0]

					if "terms" in existsing:
						terms = existsing["terms"]

				if not objectList["term"]["value"] in terms:
					terms.append(objectList["term"]["value"])

				element = {
					"ressource_id" : str(row["ressource_id"]),
					"school_id" : str(row["school_id"]),
					"branch_id" : str(row["branch_id"]),
					"title" : row["title"],
					"name" : row["name"],
					"terms" : terms
				}

				status = sync.sync(db.ressources, unique, element)

				'''if sync.check_action_event(status) == True:
					for url in sync.find_listeners('ressource', unique):
						sync.send_event(url, status["action"], element)

					for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
						sync.send_event(url, "ressource", element)

					for url in sync.find_general_listeners('ressource_general'):
						sync.send_event(url, status["action"], element)'''

			deleted = sync.find_deleted(db.ressources, {"school_id" : school_id, "branch_id" : branch_id}, ["ressource_id"], objectList["ressources"])

			'''for element in deleted:
				for url in sync.find_listeners('ressource', {"ressource_id" : element["ressource_id"]}):
					sync.send_event(url, 'deleted', element)

				for url in sync.find_listeners('school', {"school" : school_id, "branch_id" : branch_id}):
					sync.send_event(url, "ressource_deleted", element)'''


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