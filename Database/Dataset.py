import uuid

from sqlalchemy import Column, String

from Database.Engine import Base, dbSession, engine


class Dataset(Base):
    __tablename__ = 'Datasets'
    __table_args__ = {'extend_existing': True}
    id = Column('id', String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True, nullable=False)
    userUUID = Column('userId', String(length=36))

    def saveToDB(self):
        dbSession.add(self)
        dbSession.commit()


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
