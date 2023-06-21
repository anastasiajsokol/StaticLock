/**
 *  Static Lock Keyring
 *      updated: June 21st, 2023
 *      author: Anastasia Sokol
 *      version: 0.2
**/

// PBKDF2 hash as Uint8Array
async function hash(password, salt){
    const enc = new TextEncoder();
    
    return window.crypto.subtle.deriveBits(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 480000,
            hash: "SHA-256",
        },
        await window.crypto.subtle.importKey(
            "raw",
            enc.encode(password),
            { name: "PBKDF2" },
            false,
            ["deriveBits"]
        ),
        256
    ).then(buffer => {
        return new Uint8Array(buffer);
    });
}

class Keyring {
    constructor(){
        // ensure the service worker design is even possible
        if(!("serviceWorker" in navigator && window.crypto?.subtle)){
            throw new Error("unable to create static lock keyring without service worker support!");
        }

        // attempt to load map (made public in case supervisory code wishes to update or retry in case of error)
        // note that this.map is a Promise, not a 'real' value
        this.reloadmap();
    }

    reloadmap(){
        this.map = fetch("map.json").then(res => res.json()).then(map => {
            // ensure the versions match (also decreases the chances of an unintentional resource name overlap not being detected till later)
            if(map.version != "0.2"){
                throw new Error(`map.json version mismatch [expected 0.2 but got ${map.version}]`);
            }
            return map;
        }).catch(error => {
            console.error(`map Load Failed [${error}]`);
            return { valid: false };
        });
    }

    verify(password, scope){
        return this.map.then(async map => {
            // ensure structure
            if(!map.valid){
                throw new Error("currently keyring holds an invalid map (see keyring.reloadmap)");
            } else if(!map.scopes[scope]){
                throw new Error("scope not found in current map, perhaps the current map object is out of date (see keyring.reloadmap)");
            }

            // unpack salt and hash (decode and ensure they exist)
            const exists = (value) => { if(!value){ throw new Error(`invalid path object at map path ${scope}`); } return value; }
            const decode = (value) => { value = atob(value); return new Uint8Array(value.length).map((_, i, __) => value.charCodeAt(i)); }
            let passwordsalt = decode(exists(map.scopes[scope].salts?.password));
            let passwordhash = decode(exists(map.scopes[scope].passwordhash));

            // get hash as Uint8Array
            const hashbuffer = await hash(password, passwordsalt);

            // compare hash to provided prehashed password
            if(hashbuffer.byteLength != passwordhash.byteLength){
                return false;
            }

            for(let i = 0; i < hashbuffer.length; ++i){
                if(hashbuffer[i] !== passwordhash[i]){
                    return false; }
            }

            return true;
        });
    }
};

if(window.keyring){
    console.warn("static lock keyring: window.keyring already set... saving the current value to window._keyring");
    window._keyring = window.keyring;
}

window.keyring = new Keyring();