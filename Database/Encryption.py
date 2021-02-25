import os

import settings
import base64
from Cryptodome.Cipher import AES
from Cryptodome import Random

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]

def encryptData(raw):
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(bytes(os.getenv('FERNET_KEY'), encoding='utf-8'), AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw.encode("utf8")))


def decryptData(enc):
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(bytes(os.getenv('FERNET_KEY'), encoding='utf-8'), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:])).decode("utf-8")


if __name__ == '__main__':
    print(encryptData('Hello World'))
    print(decryptData(encryptData('Hello World')))
