import database
import datetime
import error
db = database.db

# Inserts the data if it doesn't exits, skips if a match exists and updates if it exists but in an older version
def sync ( table, query, document, unset=["_updated", "_id", "_created"] ):
	existsing = table.find(query).limit(1)

	if existsing.count() is 0:
		document["_created"] = datetime.datetime.now()
		try:
			table.update(query, document, upsert=True)
		except Exception, e:
			error.log(__file__, False, str(e))
		return {
			"status" : True,
			"action" : "created"
		}
	else:
		existsing = existsing[0]
		try:
			for item in unset:
				document.pop(item, None)
				existsing.pop(item, None)

			difference = set(document.iteritems())-set(existsing.iteritems())

			if len(difference) == 0:
				return {
					"status" : True,
					"action" : "existsing"
				}
		except Exception, e:
			error.log(__file__, False, str(e))
		document["_updated"] = datetime.datetime.now()
		try:
			table.update(query, document, upsert=True)
		except Exception, e:
			error.log(__file__, False, str(e))
		return {
			"status" : True,
			"action" : "updated",
			"difference" : difference
		}

# Checks if to fire an event based on the status of
def check_action_event ( status ):
	if not "status" in status or not "action" in status:
		return False

	if status["status"] == False or status["action"] == "existsing":
		return False

	return True

'''
	Retrieves a list of event listeners for the specific object type,
	and where the data matches the quer, a list of URLs is returned
'''
def find_listeners ( type, query ):
	listeners = db.event_listeners.find({
		"type" : type,
		"query" : query
	})

	urls = []

	for listeners in listeners:
		urls = urls + listeners["urls"]

	return urls

def find_general_listeners ( type ):
	listeners = db.event_listeners.find({
		"type" : type
	})

	urls = []

	for listeners in listeners:
		urls = urls + listeners["urls"]

	return urls

def send_event ( url, event, data ):
	pass