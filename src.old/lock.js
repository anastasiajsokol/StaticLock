/**
 *  Create service workers only on specific scope!
 *      This way every worker can have a different hash ability
 * 
 *  Switch to using AES-GCM
**/

/*
async function install_service_worker(){
    if("serviceWorker" in navigator){
        try {
            const registration = await navigator.serviceWorker.register("/lockworker.js", {
                scope: "/",
                type: "module"
            });

            if (registration.installing) {
            console.log("Service worker installing");
            } else if (registration.waiting) {
                console.log("Service worker installed");
            } else if (registration.active) {
                console.log("Service worker active");
            }
        } catch (error) {
            console.error(`Registration failed with ${error}`);
        }
    } else {
        console.error("Service Workers not supported in browser");
    }
}

install_service_worker();
*/
