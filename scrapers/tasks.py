from celery import Celery
import config

app.conf.BROKER_URL = 'mongodb://%:%@%:%/%' % (config.database_username, config.database_password ,config.database_host, config.database_port, config.database_name)

app.conf.CELERY_RESULT_BACKEND = 'mongodb://%:%@%:%s/%s' % (config.database_username, config.database_password ,config.database_host, config.database_port, config.database_name)
app.conf.CELERY_MONGODB_BACKEND_SETTINGS = {
    'database': 'celery',
    'taskmeta_collection': 'celery_taskmeta',
}

app = Celery('tasks', backend=CELERY_RESULT_BACKEND, broker=BROKER_URL)

@app.task
def schools ():
	from importers import importSchools

	importSchools.importSchools()
