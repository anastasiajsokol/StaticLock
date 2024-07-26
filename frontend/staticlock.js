/*
    StaticLock v4 Frontend WebWorker
        repository  https://github.com/anastasiajsokol/StaticLock
        author      Anastasia Sokol
        lisense     The Unliscense (see repository for more information)
*/

self.addEventListener("activate", (event) => {
    event.waitUntil(clients.claim());
    console.log("Active");
});