/**
 *  Static Lock Service Worker Key
 *      updated: June 21st, 2023
 *      author: Anastasia Sokol
 *      version: 0.2
**/

/**
 *  check access to the SubtleCrypto API - without access the service worker should fail to install
**/
if(!self.crypto.subtle){
    console.error("static lock key installation failed - requires access to SubtleCrypto API");
    throw new Error("the static lock service worker key can not be registered without the SubtleCrypto API");
}

/**
 *  setup and load index database
 *      note that this is required for worker functionality and should fail to register if it fails
**/

if(!self.indexedDB){
    console.error("static lock key installation failed - requires access to indexedDB api");
    throw new Error("the static lock service worker key can not be registered without the indexedDB API");
}

const indexdb = new Promise(resolve => {
    const dbregistration = self.indexedDB.open("keydb", 0.2 * 100); // version 0.2, modified by 100 to support 3 version digits (ex 0.200 can be different from 0.201, but not 0.2001!)

    dbregistration.onupgradeneeded = event => {
        const keystore = event.target.result.createObjectStore("keys", { keyPath: "scope" });
        keystore.createIndex("scope", "scope", {unique: true});
    };

    dbregistration.onabort = event => {
        throw new Error(`unable top open key database [${event.target.result}]`);
    };

    dbregistration.onsuccess = event => {
        resolve(event.target.result);
    };
});

/**
 *  Create simple object to store and retrieve the decryption key between sessions
 *      Note that if a key is not set, undefined is returned
 *      By design only 'message' events should register keys (this is not enforced)
**/
const db = {
    _keys: {},
    
    map: fetch('map.json').then(map => map.json()).catch(error => {
        console.error(`lock service worker failed to load map ${error}`);
        return {valid: false};
    }),

    async getkey(scope){
        // fetch and cache from indexed database if not already cached
        if(!(scope in this._keys)){
            this._keys[scope] = await new Promise(resolve => {
                indexdb.then(db => {
                    const transaction = db.transaction("keys", "readonly");
                    const store = transaction.objectStore("keys");
                    const request = store.get(scope);
                    request.onsuccess = event => {
                        resolve(event.target.result?.key);
                    };
                    request.onabort = _ => {
                        console.warn(`unable get key from database`);
                        resolve(undefined);
                    };
                });
            });
        }

        // return cache
        return this._keys[scope];
    },

    async setkey(scope, key){
        // set local cache
        this._keys[scope] = key;

        // save to indexed database
        await new Promise(resolve => {
            indexdb.then(db => {
                const transaction = db.transaction("keys", "readwrite");
                const store = transaction.objectStore("keys");
                const data = {
                    key: key,
                    scope: self.registration.scope
                };
                store.add(data);
                resolve(data);
            });
        });
    }
};

async function getDecryptionInformation(url){
    const map = await db.map;

    if(!map.valid){
        throw new Error("Unable to glean decryption information from an invalid map");
    }
    
    url = new URL(url);

    let scope = url.pathname.split("/");
    let file = '/' + scope.pop();

    while(scope.length){
        const joined_scope = scope.join("/");
        if(joined_scope in (map.scopes ?? {})){
            if(file in (map.scopes[joined_scope].files ?? {})){
                let key = await db.getkey(joined_scope);
                
                if(key === undefined){
                    console.warn("attempt to access encrypted scope which has not yet been unlocked, defaulting to raw");
                    return {type: "raw"};
                }

                const decode = (value) => { value = atob(value); return new Uint8Array(value.length).map((_, i, __) => value.charCodeAt(i)); }

                return {
                    type: "AESGCM",
                    key: key,
                    iv: decode(map.scopes[joined_scope].files[file].iv),
                    tag: decode(map.scopes[joined_scope].files[file].tag),
                };
            }

            console.warn("unregistered file in encrypted scope, defaulting to raw - map.json may be outdated or invalid");
            return { type: "raw" };
        }

        file = '/' + scope.pop() + file;
    }

    return {type: "raw"};
}

/**
 *  Accept decryption keys from keyring
**/
self.addEventListener("message", event => {
    const data = event.data;
    
    if(data.version !== "0.2"){
        console.error(`static lock service worker recieved a message with invalid version metadata (expects version "0.2", got ${data.version})`);
        return;
    }

    if(data.action === "store"){
        if(!data.key || !data.scope){
            throw new Error("the store action requires both a key and a scope");
        }

        db.setkey(data.scope, data.key);
    } else {
        console.warn("static lock service worker - unsure what to do with message", data);
    }
}, {
    passive: true
});

/**
 *  Install service worker by storing key from message event
**/
self.addEventListener("install", event => {
    console.log(`installing static lock key worker on ${self.registration.scope}`);
    self.skipWaiting();
});

/**
 *  Claim all clients (in scope) when activated
**/
self.addEventListener("activate", event => {
    console.log(`activating static lock key worker on ${self.registration.scope}`);
    clients.claim();
});

/**
 *  Decrypt response body before returning
**/
self.addEventListener("fetch", (event) => {
    event.respondWith((async _ => {
        const info = await getDecryptionInformation(event.request.url);
        return fetch(event.request).then(async response => {
            if(info.type === 'AESGCM'){
                const body = new Uint8Array(await response.arrayBuffer());

                const cyphertext = new Uint8Array(body.length + info.tag.length);
                cyphertext.set(body);
                cyphertext.set(info.tag, body.length);

                return self.crypto.subtle.decrypt({
                    name: "AES-GCM",
                    iv: info.iv,
                    tagLength: 128,
                    data: body
                }, info.key, cyphertext).then(decrypted_body => {
                    return new Response(decrypted_body, response);
                });
            }

            return response;
        });
    })());
});
