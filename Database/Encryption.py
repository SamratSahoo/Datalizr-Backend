import binascii
import sys

from cryptography.fernet import Fernet
import os
import settings


def encryptData(data):
    key = os.getenv('FERNET_KEY')
    fernet = Fernet(key.encode())
    return fernet.encrypt(bytes(data, encoding='utf-8'))


def decryptData(encryption):
    key = os.getenv('FERNET_KEY')
    fernet = Fernet(key.encode())
    return fernet.decrypt(encryption).decode()


if __name__ == '__main__':
    print(decryptData(encryptData('Hello World')))
