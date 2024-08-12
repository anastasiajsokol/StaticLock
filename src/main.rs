/*
    StaticLock v4
        repository  https://github.com/anastasiajsokol/StaticLock
        author      Anastasia Sokol
        lisense     The Unliscense (see repository for more information)
*/

use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm, Key, Nonce,
};

#[derive(Debug)]
struct DecryptionKey {
    key: Key<Aes256Gcm>,
    nonce: Vec<u8>,
}

fn encrypt_file(path: &String) -> Result<DecryptionKey, std::io::Error> {
    // generate key and cipher
    let key: Key<Aes256Gcm> = Aes256Gcm::generate_key(OsRng);

    let cipher = Aes256Gcm::new(&key);
    let nonce = Aes256Gcm::generate_nonce(&mut OsRng);

    let plaintext: &[u8] = &std::fs::read(&path)?;

    let ciphertext = cipher
        .encrypt(&nonce, plaintext)
        .expect("Failed to encrypt");

    std::fs::write(&path, ciphertext)?;

    Ok(DecryptionKey {
        key: key,
        nonce: nonce.to_vec(),
    })
}

fn decrypt_file(path: &String, key: &DecryptionKey) -> Result<(), std::io::Error> {
    let ciphertext: &[u8] = &std::fs::read(&path)?;

    let cipher = Aes256Gcm::new(&key.key);
    let nonce = Nonce::from_slice(&key.nonce);

    let plaintext = cipher.decrypt(&nonce, ciphertext).expect("Failed to decrypt");

    std::fs::write(&path, plaintext)?;

    Ok(())
}

fn main() {
    let path: String = "poem.txt".into();

    let key = encrypt_file(&path).expect("oh no!");

    println!("{:?}", key);

    std::io::stdin().read_line(&mut String::new()).expect("input error...");

    decrypt_file(&path, &key).expect("no oh!");
}
