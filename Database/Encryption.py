import os
import settings

from cryptography.fernet import Fernet

def encryptData(data):
    fernet = Fernet(bytes(os.getenv('FERNET_KEY'), encoding='utf8'))
    return fernet.encrypt(bytes(data, encoding='utf8'))


def decryptData(encryption):
    fernet = Fernet(bytes(os.getenv('FERNET_KEY'), encoding='utf8'))
    return fernet.decrypt(encryption).decode("utf-8")


if __name__ == '__main__':
    print(encryptData('Hello World'))
    print(decryptData(encryptData('Hello World')))
