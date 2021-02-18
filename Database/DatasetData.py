import uuid

from sqlalchemy import Column, String, PickleType, Boolean

from Database.Engine import dbSession, Base, engine


class DatasetData(Base):
    __tablename__ = 'DatasetData'
    __table_args__ = {'extend_existing': True}
    id = Column('id', String(length=36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    datasetId = Column('datasetId', String(length=36))
    data = Column('data', PickleType())
    userUUID = Column('userId', String(length=36))
    fileType = Column('fileType', String(), default=".csv")
    loaded = Column('loaded', Boolean(), default=False)

    def __repr__(self):
        return 'UUID: %r' % self.id

    def saveToDB(self):
        dbSession.add(self)
        dbSession.commit()


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    data = DatasetData(datasetId='sddsfsdfdfsdfsdfsdf', data=['Hello', 'World'], userUUID='jfhlkjhsdlfkj', fileType='.csv',
                       loaded=False)
    data.saveToDB()
    print(DatasetData.query.filter_by(loaded=False).all())
