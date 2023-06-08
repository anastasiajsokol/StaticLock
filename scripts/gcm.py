"""
    AES GCM - because fernet is a real pain :/
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from typing import Tuple
import base64
import os

# pbkdf2hmac

password = b"password"
salt = b"salt"

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)

key = kdf.derive(password)

print(base64.urlsafe_b64encode(key))

# aes gcm

def encrypt(key: bytes, message: bytes) -> Tuple[bytes, bytes, bytes]:
    """returns the GCM iv, cyphertext, and tag"""
    iv = os.urandom(96)    
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv)).encryptor()
    ct = encryptor.update(message) + encryptor.finalize()
    return (iv, ct, encryptor.tag)

def decrypt(key, iv: bytes, cyphertext: bytes, tag: bytes) -> bytes:
    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag)).decryptor()
    return decryptor.update(cyphertext) + decryptor.finalize()

iv, ct, tag = encrypt(key, b"Hello World!")
print(base64.urlsafe_b64encode(ct))
print(decrypt(key, iv, ct, tag))
