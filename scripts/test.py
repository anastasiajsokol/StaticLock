from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64

# fernet

fernet = Fernet("cw_0x689RpI-jtRR7oE8h_eQsKImvJapLeSbXpwF4e4=")
token = fernet.encrypt(b"Hello!")
print("token:", token)

# pbkdf2hmac

password = b"password"
salt = b"salt"

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)

print(base64.urlsafe_b64encode(kdf.derive(password)))