import database
import datetime
db = database.db

def log ( file, status, error ):
	db.errors.insert({
		"file" : file,
		"status" : status,
		"error" : error,
		"_created" : datetime.datetime.now(),
		"_updated" : datetime.datetime.now()
	})