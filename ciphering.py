from Crypto.Cipher import AES
from Crypto.Hash.MD5 import MD5Hash
from Crypto.Hash.SHA256 import SHA256Hash


def get_password_hash(password):
    return MD5Hash(password.encode()).digest()[:24]


def get_sha_hash(password):
    return SHA256Hash(password).hexdigest()


def encrypt(message, password):
    message_bytes = message
    rest_bytes = b'\x00' * ((16 - len(message_bytes) % 16) % 16)
    message_bytes += rest_bytes

    aes = AES.new(password)

    ciphertext = aes.encrypt(message_bytes)
    return ciphertext


def decrypt(ciphertext, password):
    aes = AES.new(password)

    return aes.decrypt(ciphertext).strip(b'\x00')
