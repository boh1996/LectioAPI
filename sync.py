import database
import datetime
import error
db = database.db

def flatten ( l ):
	out = []
	if isinstance(l, (list, tuple)):
		for item in l:
			out.extend(flatten(item))
	elif isinstance(l, (dict)):
		for dictkey in l.keys():
			out.extend(flatten(l[dictkey]))
	elif isinstance(l, (str, int, unicode)):
		out.append(l)
	return out

# Inserts the data if it doesn't exits, skips if a match exists and updates if it exists but in an older version
def sync ( table, query, document, unset=["_updated", "_id", "_created"] ):
	existsing = table.find(query).limit(1)

	if existsing.count() is 0:
		document["_created"] = datetime.datetime.now()
		document["_updated"] = datetime.datetime.now()
		try:
			_id = table.insert(document, manipulate=True)
		except Exception, e:
			error.log(__file__, False, str(e))
		return {
			"status" : True,
			"action" : "created",
			"_id" : _id
		}
	else:
		existsing = existsing[0]
		difference = None
		unsettedRows = {}
		_id = None
		try:
			for item in unset:
				if item in existsing:
					unsettedRows[item] = existsing[item]
					existsing.pop(item, None)
				if item in document:
					document.pop(item, None)

			existingRows = []

			for row in document:
				if row in existsing:
					existingRows.append(existsing[row])

			for row in existsing:
				if not row in document:
					document[row] = existsing[row]

			existingItems = []
			documentItems = []

			for row in document:
				row = " ".join(flatten(document[row]))

				documentItems.append(row)

			for row in existingRows:

				row = " ".join(flatten(row))

				existingItems.append(row)

			difference = set(documentItems)-set(existingItems)

			if len(difference) == 0:
				return {
					"status" : True,
					"action" : "existsing",
					"_id" : unsettedRows["_id"]
				}
		except Exception, e:
			error.log(__file__, False, str(e))

		for item in unsettedRows:
			if item in unsettedRows and not unsettedRows[item] == None:
				document[item] = unsettedRows[item]

		# Assign updated Time
		document["_updated"] = datetime.datetime.now()

		# If no created field, create it
		if not "_created" in document:
			document["_created"] = datetime.datetime.now()

		# Update Table
		try:
			table.update(query, document, upsert=True)

			_id = unsettedRows["_id"]
		except Exception, e:
			error.log(__file__, False, str(e))

		return {
			"status" : True,
			"action" : "updated",
			"difference" : difference,
			"_id" : _id
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

def find_deleted ( table, query, uniqueRows, current ):
	deleted = []

	existsing = table.find(query)

	if existsing is None:
		return deleted

	for row in existsing:
		found = False
		for element in current:
			if same(uniqueRows, element, row):
				found = True

		if not found:
			table.remove({
				"_id" : row["_id"]
			})
			deleted.append(row)

	return deleted

def same ( uniqueRows, element1, element2 ):
	same = True
	for row in uniqueRows:
		if not row in element1 and row in element2:
			same = False

		if not row in element2 and row in element1:
			same = False

		if row in element1 and row in element2:
			if type(element2[row]) == type(element1[row]):
				if not element2[row] == element1[row]:
					same = False
			else:
				if not str(element2[row]) == str(element1[row]):
					same = False

	return same