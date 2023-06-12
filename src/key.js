/**
 *  Static Lock Service Worker Key
 *      updated: June 11th, 2023
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

const indexdb = self.indexedDB.open("keydb", 0.2 * 100); // version 0.2, modified by 100 to support 3 version digits (ex 0.200 can be different from 0.201, but not 0.2001!)

indexdb.onupgradeneeded = event => {
    const keystore = indexdb.createObjectStore("keys", { keyPath: "scope" });
    keystore.createIndex("scope", "scope", {unique: true});
};

indexdb.onerror = event => {
    throw new Error(`unable top open key database [${event}]`);
}

/**
 *  Create simple object to store and retrieve the decryption key between sessions
 *      Note that a key must be set before retrieved
 *      By design only the 'install' event handler should set the key (paired with initial 'message' event)
**/
const db = {
    async getkey(){
        // fetch and cache from indexed database if not already cached
        if(!this._key){
            this._key = await new Promise(resolve => {
                const transaction = indexbd.transaction("keydb", "readonly");
                const store = transaction.objectStore("keydb");
                const request = store.get(self.scope);
                request.onsuccess = event => {
                    resolve(event.target.result.key);
                };
                request.onerror = event => {
                    throw new Error(`unable get key from database [${event}]`);
                };
            });
        }

        // return cache
        return this._key;
    },

    async setkey(key){
        // set local cache
        this._key = key;

        // save to indexed database
        await new Promise(resolve => {
            const transaction = indexdb.transaction("keydb", "readwrite");
            const store = transaction.objectStore("keydb");
            const data = {
                key: key,
                scope: self.scope
            };
            store.add(data);
            resolve(data);
        });
    }
};

self.addEventListener("install", event => {
    event.waitUntil(async () => {
        const key = await new Promise(resolve => {
            function handler(event){
                if(event.data.key){
                    self.removeEventListener("message", handler, { passive: true });
                    resolve(event.data.key);
                } else {
                    console.warn("static lock key service worker received message without key metadata");
                }
            }

            self.addEventListener("message", handler, { passive: true });
        });

        await db.setkey(key);

        console.log("static lock key installed");
    });
});

self.addEventListener("activate", event => {
    event.waitUntil(clients.claim());
    console.log("static lock key activated");
});