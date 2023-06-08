async function decrypt(cyphertext, tag, key, iv){
    const data = new Uint8Array(cyphertext.length + tag.length);
    data.set(cyphertext);
    data.set(tag, cyphertext.length);
    
    return window.crypto.subtle.decrypt({
            name: "AES-GCM",
            data: cyphertext,
            iv: iv,
            tagLength: 128
        },
        await window.crypto.subtle.importKey(
            "raw",
            key,
            { name: "AES-GCM" },
            false,
            ["decrypt"]
        ),
        data
    ).then(buffer => {
        return new TextDecoder().decode(buffer);
    });
}

const base64_to_buffer = (value) => {
    value = atob(value);
    const buffer = new Uint8Array(value.length);
    for(let i = 0; i < value.length; ++i){
        buffer[i] = value.charCodeAt(i);
    }
    return buffer;
};

let iv = base64_to_buffer("Ei2QM33Pu6HwxMv+mlszsQw2ybhzVf2ZdUeexBY6pK2E5drZnWKqC3BdcLjLs6g80+UbJvnHhO30tcR2dymixwWo2VixUWE6dbVsJ73ctHcp9MQ5hH98/O4A4rG1JSY9");
let key = base64_to_buffer("e9ZDKH5R62+gUogecGokb6ueLHRnp/dSB90OyZsJnHs=");
let tag = base64_to_buffer("oybXzc4mXA9xX+JwfnaFog==");
let cyphertext = base64_to_buffer("Dh6skVazJG39Umj8");

decrypt(cyphertext, tag, key, iv).then(res => {
    console.log("decrypted:", res);
});