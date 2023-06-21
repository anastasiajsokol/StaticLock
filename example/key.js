/**
 *  Static Lock Service Worker Key
 *      updated: June 21st, 2023
 *      author: Anastasia Sokol
 *      version: 0.2
**/

/**
 *  setup and load index database
 *      note that this is required for worker functionality and should fail to register if it fails
**/

if(!self.indexedDB){
    console.error("static lock key installation failed - requires access to indexedDB api");
    throw new Error("the static lock service worker key can not be registered without the indexedDB api");
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
                        resolve(event.target.result.key);
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

/**
 *  Accept decryption keys from keyring
**/
self.addEventListener("message", event => {
    if(event.data.key && event.data.scope && event.data.version == "0.2"){
        console.log(`setting key ${event.data.key}`);
        db.setkey(event.data.scope, event.data.key);
    } else if(event.data.version != undefined && event.data.version != "0.2"){
        console.error(`message to key service worker version "0.2" had version meta data ${event.data.version}`);
    } else {
        console.warn("static lock key service worker received message without valid key data");
    }
}, {
    passive: true
});

/**
 *  Install service worker by storing key from message event
**/
self.addEventListener("install", event => {
    console.log(`installing static lock key worker on ${self.registration.scope == '/' ? "global scope" : self.registration.scope}`);
    self.skipWaiting();
});

/**
 *  Claim all clients (in scope) when activated
**/
self.addEventListener("activate", event => {
    console.log(`activating static lock key worker on ${self.registration.scope == '/' ? "global scope" : self.registration.scope}`);
    clients.claim();
});

/**
 *  Decrypt response body before returning
**/
self.addEventListener("fetch", (event) => {
    console.warn("currently just a raw fetch");
    return fetch(event.request);
});
