import uuid

from sqlalchemy import Column, String, PickleType, Boolean, Integer

from Database.Engine import dbSession, Base, engine


class DataReview(Base):
    __tablename__ = 'DataReview'
    __table_args__ = {'extend_existing': True}
    id = Column('id', String(length=36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    datasetId = Column('datasetId', String(length=36))
    userId = Column('userId', String(length=36))
    dataId = Column('dataId', String(length=36))
    approvalStatus = Column('approvalStatus', Boolean())

    def __repr__(self):
        return 'UUID: %r' % self.id

    def saveToDB(self):
        dbSession.add(self)
        dbSession.commit()
