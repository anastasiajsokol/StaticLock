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

        // register a decryption worker on the global scope
        // because static lock is designed for static sites, the worker will also cache responses by default
        this.worker = navigator.serviceWorker.register("key.js", {
            scope: "/",
            updateViaCache: "none"
        });

        // attempt to load map (made public in case supervisory code wishes to update or retry in case of error)
        // note that this.map is a Promise, not a 'real' value
        this.reloadMap();
    }
    
    reloadMap(){
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

    verifyPassword(scope, password){
        return this.map.then(async map => {
            // ensure structure is ok
            if(!map.valid){
                throw new Error("currently keyring holds an invalid map (see keyring.reloadmap)");
            } else if(!map.scopes[scope]){
                throw new Error("scope not found in current map, perhaps the current map object is out of date (see keyring.reloadmap)");
            }

            // unpack salt and hash (decode and ensure they exist)
            const exists = (value) => { if(!value){ throw new Error(`invalid scope object at map path ${scope}`); } return value; }
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
                    return false;
                }
            }

            return true;
        });
    }

    async registerScope(scope, password){
        // get site map and ensure scope is registered
        const map = await this.map;
        
        if(!map.valid){
            throw new Error("invalid map - try Keyring.reloadMap before attempting again");
        }

        if(map.scopes[scope] === undefined){
            throw new Error("cannot register password for scope that is not in map, try Keyring.reloadMap to refresh cache in case of outdated version");
        }

        // verify password - this is for UI, not a security measure
        if(!await this.verifyPassword(scope, password)){
            throw new Error(`cannot register invalid password onto scope ${scope}`);
        }

        // read salt from site map
        const exists = (value) => { if(!value){ throw new Error(`invalid scope object at map path ${scope}`); } return value; }
        const decode = (value) => { value = atob(value); return new Uint8Array(value.length).map((_, i, __) => value.charCodeAt(i)); }
        const salt = decode(exists(map.scopes[scope].salts?.data));

        // generate key from password hash
        const key = await window.crypto.subtle.importKey("raw", await hash(password, salt), { name: "AES-GCM" }, false, ["decrypt"]);

        // get current worker
        const worker = await this.worker.then(res => { return res.installing || res.waiting || res.active; });

        // send store request
        worker.postMessage({
            version: "0.2",
            action: "store",
            scope: scope,
            key: key
        });
    }

    setCacheBehavior(style){

    }
};

if(window.keyring){
    console.warn("static lock keyring: window.keyring already set... saving the current value to window._keyring");
    window._keyring = window.keyring;
}

window.keyring = new Keyring();