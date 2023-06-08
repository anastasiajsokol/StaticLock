class Keyring {
    constructor(){
        if(!("serviceWorker" in navigator)){
            throw Error("Static Lock: unable to create keyring without service worker support!");
        }
        
        // load map.json from root
        this.loadmap();
    }

    loadmap(){
        this.map = fetch("/map.json").then(res => {
            if(res.statusText == "OK"){
                return res.json();
            } else {
                throw Error("Network error - failed to load map");
            }
        }).then(map => {
            function assertvalid(condition, message = "Invalid Map"){
                if(!condition){ console.error(map); throw new Error(message); }
            }

            assertvalid(map.version === '0.2', `invalid map version [expected 0.2, got ${map.version}]`);
            assertvalid(typeof(map.paths) === "object", "map.paths missing or corrupted");

            for(const path in map.paths){
                let obj = map.paths[path];
                assertvalid(typeof(obj.passwordhash) === "string", "passwordhash missing from path");
                assertvalid(typeof(obj.salts) === "object", "missing or corrupted salts profile");
                assertvalid(typeof(obj.salts.password) === "string", "incomplete salts profile - password");
                assertvalid(typeof(obj.salts.data) === "string", "incomplete salts profile - data");
                assertvalid(typeof(obj.files) === "object", "obj.files missing or corrupted");
                for(let file of obj.files){
                    assertvalid(typeof(file.path) === "string", `file in path ${path} missing file path`);
                    assertvalid(typeof(file.iv) === "string", `file in path ${path} missing or invalid iv`);
                    assertvalid(typeof(file.tag) === "string", `file in path ${path} missing or invalid tag`);
                }
            }
            return map;
        }).catch(error => {
            console.error(`There was an error loading the keyring map! [${error}]`);
            return { valid: false };
        });
    }

    register(password, scope){
        return this.map.then(async map => {
            if(!map.valid){
                throw new Error("Currently loaded map is not valid");
            } else if(map.paths[scope] === undefined){
                throw new Error(`Scope ${scope} is not a valid map path`);
            }
            
            const enc = new TextEncoder();

            const key = await window.crypto.subtle.importKey(
                "raw",
                enc.encode(password),
                { name: "PBKDF2" },
                false,
                ["deriveBits"]
            );

            return window.crypto.subtle.deriveBits(
                {
                    name: "PBKDF2",
                    salt: enc.encode(map.paths[scope].salts.password),
                    iterations: 480000,
                    hash: "SHA-256",
                },
                key, 256
            ).then(buffer => new Uint8Array(buffer)).then(async buffer => {
                let hash = atob(map.paths[scope].passwordhash);
                if(buffer.byteLength != hash.length){ throw Error(`Invalid password hash in map for scope ${scope}`); }
                for(let i = 0; i < hash.length; ++i){
                    if(buffer[i] != hash.charCodeAt(i)){
                        console.log(`fail at ${i} (${buffer[i]} != ${hash.charCodeAt(i)})`);
                        return false;
                    }
                }

                // register service worker to scope
                console.warn("No service worker registered! Use keyring.fetch(scope, path)");

                let scopekey = await window.crypto.subtle.deriveBits(
                    {
                        name: "PBKDF2",
                        salt: enc.encode(map.paths[scope].salts.data),
                        iterations: 480000,
                        hash: "SHA-256",
                    },
                    key, 256
                );

                map.paths[scope].key = scopekey;
                
                return true;
            });
        });
    }

    fetch(scope, path, init = undefined){
        return this.map.then(async map => {
            if(!map.valid){ throw new Error("invalid page map - see keyring.loadmap"); }
            else if(map.paths[scope] === undefined){ throw new Error(`No scope ${scope} in page map`); }
            else if(map.paths[scope].key === undefined){ throw new Error(`No key associated with scope ${scope} - see keyring.register`); }

            return fetch(scope + "/" + path, init).then(response => { 
                // TODO figure out how to decrypt the body while (symbolically) preserving the request object
                console.warn("Decryption not implimented!");
                return response;
            });
        });
    }
};

window.keyring = new Keyring();