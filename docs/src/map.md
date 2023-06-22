# Static Lock Page Map Version 0.2

    Must be located at 'map.json' in root web directory

    To generate use scripts/encrypt.py as described in docs/scripts/encrypt.md

## Structure

    valid: bool
        should be true, in case of an error must be switched to false
    
    version: string
        must match version of both encryption and decryption tools, currently '0.2'
    
    scopes: object
        indexed by scopes, contains scope objects as described below
        index scopes must begin with a slash '/'

## Scope Objects

    passwordhash: string (base64)
        base64 encoded salted hash of the scope password, must not be the same as the key (aka the password salt and data salt must be different); should be used for UI password verification
    
    salts: object
        password: string (base64)
            base64 'passwordhash' salt, used with passwordhash for UI password verification
            WARNING: MUST NOT BE THE SAME AS THE DATA SALT
        
        data: string (base64)
            base64 data encryption salt, used to generate decryption key
            WARNING: MUST NOT BE THE SAME AS THE PASSWORD SALT
    
    files: list
        contains file objects as described below

## File Objects

    path: string (path)
        resource path relative to parent scope, describes uri of file
        must begin with '/'
    
    tag: string (base64)
        AES GCM verification tag, 128 bits, needed for file decryption
    
    iv: string (base64)
        AES GCM initialization vector (96 bytes), needed for file decryption
