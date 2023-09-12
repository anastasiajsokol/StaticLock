from types import Tuple

from .. import response

def hash(password: bytes, salt: bytes) -> Tuple[bytes, bytes]:
    return b''

def encrypt_file(source: str, destination: str, key: bytes) -> response.Response:
    return