import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import settings

# Database setup
# Sqlite will just come from a file
# package_dir = os.path.abspath(os.path.dirname(__file__))
# dbPath = os.path.join(package_dir, 'test.db')
# engine = create_engine('sqlite:///' + dbPath, connect_args={'check_same_thread': False})
engine = create_engine('mysql+mysqlconnector://' + os.getenv('DB_URL'))
dbSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = dbSession.query_property()

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
