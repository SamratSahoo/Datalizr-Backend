import datetime
import os
import uuid

from itsdangerous import SignatureExpired, BadSignature, TimedJSONWebSignatureSerializer
from sqlalchemy import Column, String, Boolean, LargeBinary
from Database.Engine import Base, dbSession


class GoogleUser(Base):
    __tablename__ = 'GoogleUsers'
    __table_args__ = {'extend_existing': True}
    # Datalizr Specific
    id = Column('id', String(length=36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Google Specific
    socialId = Column('googleId', String(200), nullable=False, unique=True)
    emailHash = Column('emailHash', String(200), unique=True)

    # Pertains to Functionality
    username = Column('username', String(100), index=True)
    admin = Column('admin', Boolean(), nullable=False, default=False)
    loginDate = Column('login', String(128), default=datetime.date.today())

    def __repr__(self):
        return 'User: %r' % self.username

    def generateAuthToken(self, expiration=3600):
        serializer = TimedJSONWebSignatureSerializer(os.getenv('APP_SECRET_KEY'), expires_in=expiration)
        return serializer.dumps({'emailHash': self.emailHash})

    @staticmethod
    def verifyAuthToken(token):
        s = TimedJSONWebSignatureSerializer(os.getenv('APP_SECRET_KEY'))
        try:
            data = s.loads(token)
        except SignatureExpired:
            return "Expired"  # valid token, but expired
        except BadSignature:
            return "Bad"  # invalid token
        user = GoogleUser.query.get(data['emailHash'])
        return user

    def saveToDB(self):
        dbSession.add(self)
        dbSession.commit()