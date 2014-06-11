import config
from pymongo import *

if hasattr(config, "database_username") and not config.database_username == "":
	db = MongoClient('mongodb://%s:%s@%s/%s' %(config.database_username, config.database_password, config.database_host, config.database_name) )
else:
	db = MongoClient(config.database_host, 27017 ).lectio