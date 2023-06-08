"""
    Static Lock Encryption Tool
        updated: June 8th, 2023
        author: Anastasia Sokol
        version: 0.2
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from typing import Tuple
import argparse
import base64
import json
import os

VERSION = "0.2"

def hash(password: str) -> Tuple[bytes, bytes]:
    """Generate hash with random salt from password, returns (hash, hashsalt)"""
    salt = os.urandom(18) # note that this does not need to be cryptographic randomness
    hash = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    ).derive(password.encode("utf-8"))
    return (hash, salt)

def create_encrypted_file(search: str, destination: str, key: bytes) -> Tuple[bytes, bytes]:
    """Encrypt file in 1024 byte chunks and save to destination, returns (iv, tag)"""
    
    # open input file first just to make sure it really exists before doing other work
    with open(search, "rb") as inputfile:
        # setup AES GCM context
        iv = os.urandom(96)
        encryptor = Cipher(algorithms.AES(key), modes.GCM(iv)).encryptor()

        # open output file
        os.makedirs(os.path.dirname(destination), exist_ok = True)
        with open(destination, "wb") as outputfile:
            # read 1kb chunks encrypting before writing
            chunk = inputfile.read(1024)
            while len(chunk):
                outputfile.write(encryptor.update(chunk))
                chunk = inputfile.read(1024)
            
            # AES GCM requires this last write! - encryption may not be valid until this happens
            outputfile.write(encryptor.finalize())
        
        # return iv and tag - these must be made public later
        return (iv, encryptor.tag)

def create_encrypted_directory(search: str, root: str, scope: str, password: str) -> dict:
    # create absolute directory path and ensure it exists
    root = os.path.join(root, scope)
    os.makedirs(os.path.dirname(root), exist_ok = True)

    # used to encrypt data, must remain private
    key, keysalt = hash(password)

    # used for UI password verification, should be made public
    passwordhash, passwordhashsalt = hash(password)

    """
        Warning: if the encryption salt and verification salt the encryption is worthless!
    """
    if keysalt == passwordhashsalt:
        print(f"Salt collision - it's your lucky day! Probability: {2 ** -18} Rehashing...")
        passwordhash, passwordhashsalt = hash(password)
        if keysalt == passwordhashsalt:
            raise SystemError("Double salt collision - most likely os.urandom is broken, or you happen to be the luckiest (or unluckiest) person to ever be born in which case try again (hopefully it works this time...) then go do something other than programming!")
    
    # convert to the general storage format (used on return and in map.json)
    # plus ensure we never accidentally use these values to encrypt later
    passwordhashsalt = base64.b64encode(passwordhashsalt).decode("utf-8")
    passwordhash = base64.b64encode(passwordhash).decode("utf-8")
    keysalt = base64.b64encode(keysalt).decode("utf-8")

    # create path map (eventually returned)
    map = {
        "passwordhash": passwordhash,
        "salts": {
            "password": passwordhashsalt,
            "data": keysalt
        },
        "files": []
    }

    for base, _, files in os.walk(search):
        # get the output location from destination root (with scope) and offset from search root and make sure it exists
        # there is probably a better way
        offset = base[len(search) + 1:]
        location = os.path.join(root, offset)

        os.makedirs(os.path.dirname(location), exist_ok = True)

        for file in files:
            iv, tag = create_encrypted_file(os.path.join(base, file), os.path.join(location, file), key)

            map["files"].append({
                "path": os.path.join(offset, file),
                "tag": base64.b64encode(tag).decode('utf-8'),
                "iv": base64.b64encode(iv).decode('utf-8')
            })
    
    return map

def dispatch(configuration: dict, verbose: bool = True, jsonindent: int = 4) -> dict:
    # make sure versions match
    if configuration["version"] != VERSION:
        raise ValueError(f"Version mismatch (expected {VERSION}, got {configuration['version']})")

    # create map
    map = {
        "valid": True,
        "version": VERSION,
        "paths": {}
    }
    
    # encrypt requested directories
    root = configuration["root"]
    for path in configuration["paths"]:
        if verbose:
            print(f"Encrypting {path['input']} to {os.path.join(root, path['scope'])}")
        map["paths"][path['scope']] = create_encrypted_directory(path["input"], root, path["scope"], path["password"])
    
    # save map to map.json in web root
    maplocation = os.path.join(root, "map.json")
    if verbose:
        print(f"Writing page map ({maplocation})")
    with open(maplocation, "w") as mapfile:
        json.dump(map, mapfile, indent=jsonindent)

if __name__ == "__main__":
    def filepath(path):
        if os.path.isfile(path):
            return path
        else:
            raise FileNotFoundError(f"File not found [{path}]")

    parser = argparse.ArgumentParser()

    parser.add_argument("-g", "--gen", help="overwrite other options, write example configuration to file", nargs='?', type=str, const="config.json")
    parser.add_argument("-c", "--config", help="configuration file path", nargs='?', type=filepath, const="config.json")
    parser.add_argument("-d", "--dev", help="show stack trace in case of exception", action="store_true")
    parser.add_argument("-s", "--silent", help="do not display progress", action="store_true")
    parser.add_argument("-i", "--indent", help="json indent size", nargs='?', type=int, default=4)

    args = parser.parse_args()

    if args.gen != None:
        if not args.silent:
            print(f"Generating default configuration to '{args.gen}'")
        with open(args.gen, "w") as file:
            # simpliest usable configuration
            json.dump({
                "version": "0.2",
                "root": "src",
                "paths": [
                    {
                        "input": "lock/locked",
                        "scope": "locked",
                        "password": "password"
                    }
                ]
            }, file, indent=args.indent)
    elif args.config != None:
        try:
            # load requested configuration and dispatch
            with open(args.config, "r") as configfile:
                config = json.load(configfile)
            dispatch(config, not args.silent, args.indent)
        except Exception as error:
            # pass on error to show stacktrace if dev specified, otherwise only print error itself
            if args.dev:
                raise error
            else:
                print(error)
    else:
        # either -h, -g, or -c must be specified
        print("Invalid combination of input parameters, use --help for more information")
