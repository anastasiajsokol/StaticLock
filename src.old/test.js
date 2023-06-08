import {base64ArrayBuffer} from "./lib/base64.js";

// fernet (OK)
var secret = new fernet.Secret("cw_0x689RpI-jtRR7oE8h_eQsKImvJapLeSbXpwF4e4=");

let data = "gAAAAABkgMKfrtLjE4DEqWZ1JOPw7a95_8maxGOqWrU3d79yxNd1vP1CFTTtjUXsZRgwI4hnNJdqWyWF4Smc_CMIfIGKwbipAQ==";

var token = new fernet.Token({
    secret: secret,
    token: data,
    ttl: 0
});

console.log(token.decode());

// pbkdf2 (OK)
async function hash(password, salt){
    const enc = new TextEncoder();

    password = enc.encode(password);
    salt = enc.encode(salt);

    return window.crypto.subtle.deriveBits(
        {
            name: "PBKDF2",
            salt,
            iterations: 480000,
            hash: "SHA-256",
        },
        await window.crypto.subtle.importKey(
            "raw",
            password,
            { name: "PBKDF2" },
            false,
            ["deriveBits"]
        ),
        256
    ).then(res => {
        return base64ArrayBuffer(res);
    });
}

hash("password", "salt").then(res => {
    console.log(res);
});
