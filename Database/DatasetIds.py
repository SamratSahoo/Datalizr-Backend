import uuid

from sqlalchemy import Column, String

from Database.Engine import dbSession, Base, engine


class DatasetIds(Base):
    __tablename__ = 'DatasetIds'
    __table_args__ = {'extend_existing': True}
    id = Column('id', String(length=36), primary_key=True, unique=True)

    def __repr__(self):
        return 'UUID: %r' % self.id

    def saveToDB(self):
        dbSession.add(self)
        dbSession.commit()

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)