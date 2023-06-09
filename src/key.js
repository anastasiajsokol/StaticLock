/**
 *  Key Service Worker
 *      updated: June 9th, 2023
 *      author: Anastasia Sokol
 *      version: 0.2
**/

self.addEventListener("fetch", event => {

});

self.addEventListener("message", event => {
    
});

self.addEventListener("install", event => {
    // in case of an outdated version claim all open pages
    clients.claim();

    // not actually implimented... ehe
    console.warn("Service worker mode not implimented!");
});
