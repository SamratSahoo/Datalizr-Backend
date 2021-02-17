from sqlalchemy import Column, String

from Database.Engine import dbSession, Base, engine


class Username(Base):
    __tablename__ = 'Username'
    __table_args__ = {'extend_existing': True}
    name = Column('name', String(length=20), primary_key=True, unique=True)

    def __repr__(self):
        return 'UUID: %r' % self.id

    def saveToDB(self):
        dbSession.add(self)
        dbSession.commit()


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
