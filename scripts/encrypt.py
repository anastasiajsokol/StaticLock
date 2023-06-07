"""
    Create a statically locked copy of a directory
    
    TODO
            CLEAN UP THIS CODE!!!!
            Change the way files are encrypted to be based on chunks
            Change the storage format from base64 to raw (even though it will have to be encoded again to decrypt)
"""

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from typing import Any
import argparse
import base64
import json
import os

class EncryptionConfiguration:
    __slots__ = ["password", "salts", "input", "output", "saltfile"]

    def __init__(self, input_directory: str, output_directory: str, saltfile: str, password: str, passwordsalt: str, filesalt: str):
        self.password = password.encode('utf-8')
        self.salts = {
            "password": passwordsalt.encode('utf-8'),
            "files": filesalt.encode('utf-8')
        }
        self.input = input_directory
        self.output = output_directory
        self.saltfile = saltfile

    def fromfile(path: str) -> Any:
        with open(path, "r") as configfile:
            config = json.load(configfile)
        
        try:
            config["password"]
            config["salts"]
            config["salts"]["password"]
            config["salts"]["files"]
            config["input"]
            config["output"]
            config["saltfile"]
        except KeyError as error:
            raise KeyError(f"Missing configuration value {str(error)}")

        return EncryptionConfiguration(config["input"], config["output"], config["saltfile"], config["password"], config["salts"]["password"], config["salts"]["files"])

def encrypt(config: EncryptionConfiguration):
    # hashing
    passwordhash = base64.urlsafe_b64encode(PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=config.salts["password"],
        iterations=480000,
    ).derive(config.password))

    encryptionhash = base64.urlsafe_b64encode(PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=config.salts["files"],
        iterations=480000,
    ).derive(config.password))

    # fernet
    fernet = Fernet(encryptionhash)

    for base, _, files in os.walk(config.input):
        root = base[len(config.input) + 1:]
        for file in files:
            # read and encrypt input file
            with open(os.path.join(base, file), "rb") as inputfile:
                data = fernet.encrypt(inputfile.read())
            # write to output file
            outputdirectory = os.path.join(config.output, root)
            os.makedirs(outputdirectory, exist_ok = True)
            with open(os.path.join(outputdirectory, file), "wb") as outputfile:
                outputfile.write(data)
    
    with open(config.saltfile, "w") as saltfile:
        json.dump({
            "version": 0.1,
            "salts": {
                "password": config.salts["password"].decode('utf-8'),
                "files": config.salts["files"].decode('utf-8')
            },
            "passwordhash": passwordhash.decode('utf-8')
        }, saltfile)

if __name__ == "__main__":
    def directory_path(string):
        if os.path.isdir(string):
            return string
        else:
            raise NotADirectoryError(string)

    def file_path(string):
        if os.path.isfile(string):
            return string
        else:
            raise FileNotFoundError(string)

    parser = argparse.ArgumentParser()

    parser.add_argument("--dev", help="show complete stack trace", action="store_true")
    parser.add_argument("-g", "--gen", help="generate default configuration file - ends operation (default name 'config.json')", nargs="?", const="config.json", type=str)

    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument("-c", "--config", help="encryption configuration file", nargs=1, type=file_path)

    args = parser.parse_args()
    
    try:
        if args.gen == None:
            if args.config == None:
                raise ValueError("Must specify a configuration file")
            encrypt(EncryptionConfiguration.fromfile(args.config[0]))
        else:
            if args.config != None:
                print("(ignoring conflicting encryption request)")
            print("generating default configuration file...")
            with open(args.gen, "w") as configfile:
                configfile.writelines([
                    '{\n',
                    '\t"password": "password",\n',
                    '\t"salts": {\n',
                    '\t\t"password": "' + base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8') + '",\n',
                    '\t\t"files": "' + base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8') + '"\n',
                    '\t},\n',
                    '\t"input": "./locked"\n',
                    '\t"input": "./src/locked"\n',
                    '\t"saltfile": "./src/salt.json"\n',
                    '}'
                ])
            print("done")
    except Exception as error:
        if args.dev:
            raise error
        print(error)
