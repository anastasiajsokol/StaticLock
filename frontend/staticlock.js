/*
    StaticLock v4 Frontend WebWorker
        repository  https://github.com/anastasiajsokol/StaticLock
        author      Anastasia Sokol
        lisense     The Unliscense (see repository for more information)
*/

// Personal State //

self.database = {
    "/frogs.say": true
};

// Initialization //

skipWaiting()

self.addEventListener("activate", (event) => {
    event.waitUntil(clients.claim());
    console.log("Active");
});

// Message and Command Handling //

self.addEventListener("message", (event) => {
    console.log("Service Worker: ", event.data);
});

// Decryption and Passthrough Handling //

self.addEventListener("fetch", (event) => {
    const request = event.request;
    let path = new URL(request.url).pathname;

    console.log("Fetching ", path);

    if(path in self.database) {
        event.respondWith(new Response("hello!"));
    } else {
        event.respondWith(fetch(request));
    }
});