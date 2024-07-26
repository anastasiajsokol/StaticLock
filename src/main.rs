/*
    StaticLock v4
        repository  https://github.com/anastasiajsokol/StaticLock
        author      Anastasia Sokol
        lisense     The Unliscense (see repository for more information)
*/

use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm
};

fn main(){
    // The encryption key can be generated randomly:
    let key = Aes256Gcm::generate_key(OsRng);

    let cipher = Aes256Gcm::new(&key);
    let nonce = Aes256Gcm::generate_nonce(&mut OsRng);
    
    let ciphertext = cipher.encrypt(&nonce, b"plaintext message".as_ref()).expect("Failed to encrypt");
    
    println!("{:?}", ciphertext);

    let plaintext = cipher.decrypt(&nonce, ciphertext.as_ref()).expect("Failed to decrypt");

    println!("{:?}", plaintext);

    assert_eq!(&plaintext, b"plaintext message");
}