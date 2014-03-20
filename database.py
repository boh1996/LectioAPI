import config
from pymongo import *

if not config.database_username == "":
	db = MongoClient('mongodb://%s:%s@%s/%s' %(config.database_username, config.database_password, config.database_host, config.database_name) )
else:
	db = MongoClient(config.database_host, 27017 ).lectio