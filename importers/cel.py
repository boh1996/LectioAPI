from __future__ import absolute_import

from celery import Celery

app = Celery('importers', backend="mongodb://localhost:27017/celery_result", broker="mongodb://localhost:27017/celery_tasks")

'''app.conf.BROKER_URL = "mongodb://localhost:27017/celery_tasks"#'mongodb://%:%@%:%/%' % (config.database_username, config.database_password ,config.database_host, config.database_port, config.database_name)

app.conf.CELERY_RESULT_BACKEND = "mongodb://localhost:27017/celery_result"#'mongodb://%:%@%:%s/%s' % (config.database_username, config.database_password ,config.database_host, config.database_port, config.database_name)
app.conf.CELERY_MONGODB_BACKEND_SETTINGS = {
    'database': 'celery',
    'taskmeta_collection': 'celery_taskmeta',
}'''
if __name__ == '__main__':
    app.start()