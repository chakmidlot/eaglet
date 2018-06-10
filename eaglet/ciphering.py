from Crypto.Cipher import AES
from Crypto.Hash.MD5 import MD5Hash
from Crypto.Hash.SHA256 import SHA256Hash


def get_sha_hash(password):
    return SHA256Hash(password).hexdigest()[:24]


class Ciphering:

    def __init__(self, password):
        self.password = get_sha_hash(password.encode())

    def ciphering_file(self, src, dst):
        with src.open('rb') as src_fp, dst.open('wb') as dst_fp:
            dst_fp.write(self.ciphering(src_fp.read()))

    def ciphering(self, message):
        raise NotImplemented


class Encryptor(Ciphering):

    def ciphering(self, message):
        message_bytes = message
        rest_bytes = b'\x00' * ((16 - len(message_bytes) % 16) % 16)
        message_bytes += rest_bytes

        aes = AES.new(self.password)

        ciphertext = aes.encrypt(message_bytes)
        return ciphertext


class Decriptor(Ciphering):

    def ciphering(self, message):
        aes = AES.new(self.password)

        return aes.decrypt(message).strip(b'\x00')
