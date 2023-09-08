# Static Lock Encryption Tool Version 0.2

## Command Line Interface

    -h / --help
        displays a help message with a loose breakdown of different options

    -g / --gen
        generates an example configuration file, defaults to 'config.json' if no name provided after command; note that this overwrites all other options except help and silent
    
    -c / --config
        reads a configuration file (required to be of the format specified below) and uses it to setup the static encryption system in the public web directory; if no file name provided defaults to 'config.json'
    
    -d / --dev
        in case of an exception shows full stack trace
    
    -s / --silent
        does not display progress to stdout, note that errors will still be reported
    
    -i / --indent
        integer for json output indentation, use 0 for most compact form, defaults to 4

## Configuration JSON Required Structure

    version: string
        configuration version string, this must match the version of the tool you are using, the current version is '0.2'
    
    root: string (path)
        file path to web root directory (may be absolute or relative)
    
    paths: list
        a list of objects which must have
            password: string
                password to encrypt path with
            input: string (path)
                path to plaintext directory to encrypt (should not be in public web directory)
            scope: string (path)
                relative path from web directory root to output directory
                please note that scopes must NOT be nested, however this case may not create an error

## Functions

```def hash(password: str) -> Tuple[bytes, bytes]:```

    Takes in a password as a string and returns a tuple containing a hashed version of the password (as a bytes object) as well as an 18 byte random salt (also as a bytes object)

    WARNING: while it is ok for the salt to be generated in a non-cryptographically random manor, it is important that any public password hashes DO NOT use the same salt as private hashes used as encryption or decryption keys

```def create_encrypted_file(search: str, destination: str, key: bytes) -> Tuple[bytes, bytes]:```

    Encrypt the file at path 'search' using the provided key into location 'destination' creating any missing directories if they do not already exist. The algorithm used is AES GCM applied to 1024 byte chunks. It is important that the key used for encryption is never made public. Returns unique IV and AES GCM tag which both must be made public for decryption. Note that the IV is generated using a non-cryptographically random source.

```def create_encrypted_directory(search: str, root: str, scope: str, password: str) -> dict:```

    Encrypts the directory at path 'search' into the provided 'scope' inside the 'root' public web directory using the provided 'password'. Returns a map.json path object as described in docs/src/map.md.

```def dispatch(configuration: dict, verbose: bool = True, jsonindent: int = 4) -> dict:```

    Takes a configuration file in the required format described above and performs the operations required to compile the unencrypted source (as described in the configuration) into encrypted scopes, as well as writes the map.json file in the root web directory as specified in docs/src/map.md. If verbose is true prints progress to stdout. Sets json indentation level to 'jsonindent', if zero uses most compact form.

## Dependencies
    psa/cryptography, typing, argparse, base64, json, and os

    Specific imports
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from typing import Tuple
        import argparse
        import base64
        import json
        import os
