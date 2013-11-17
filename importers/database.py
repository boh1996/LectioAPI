import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config

engine = create_engine(config.database+'://'+config.db_user+':'+config.db_password+'@'+config.db_host+'/'+config.db_database_name)

Session = sessionmaker(bind=engine)

# create a Session
session = Session()