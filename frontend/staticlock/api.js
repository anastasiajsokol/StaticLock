/*
    StaticLock v4 Frontend Javascript API
        repository  https://github.com/anastasiajsokol/StaticLock
        author      Anastasia Sokol
        lisense     The Unliscense (see repository for more information)
*/

// Global Configuration Semi-Constants //

window.staticlock_console = console.log;
window.staticlock_error = console.error;
window.staticlock_reporter = alert;

// Compatibility //

const StaticLockAPISupported = "serviceWorker" in navigator && typeof(Worker) !== "undefined" && typeof(window.crypto.subtle) !== "undefined";
window.StaticLockAPISupported = StaticLockAPISupported;

// Logging and Error Reporting //

window.addEventListener("load", _ => {
    if(!StaticLockAPISupported){
        window.staticlock_reporter("The StaticLock API is not supported");
    }
});

// StaticLock Object //

class StaticLock {
    constructor(){
        self.registration = navigator.serviceWorker.register("/staticlock.js", { scope: "/" })
    }

    async get_worker(){
        if(!StaticLockAPISupported){
            window.staticlock_error("Unable to get worker since StaticLock API is unsupported");
            return null;
        }

        let registration = await self.registration;

        return registration.installing || registration.waiting || registration.active;
    }
};