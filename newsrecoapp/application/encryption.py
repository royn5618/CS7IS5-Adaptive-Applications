#Encrypts and decrypts
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

BS = 16
aes_key = "94CA61A3CFC9BB7B8FF07C723917851A"

def padding(string):
	return string + " " * (AES.block_size - len(string) % AES.block_size)

class AESCipher:

	def __init__( self ):
		self.key = hashlib.sha256(aes_key.encode('utf-8')).digest()

	def encode_string(raw):
		cipher = AES.new(aes_key, AES.MODE_ECB)
		padded_data = padding(raw)
		enc = base64.b64encode(cipher.encrypt(padded_data))
		return enc

	def decode_string(enc):
		cipher = AES.new(self.key, AES.MODE_ECB)
		decoded_data = cipher.decrypt(base64.b64decode(enc))
		return decoded_data.strip()