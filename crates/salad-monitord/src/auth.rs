//! Authentication, JWT token issuance, Argon2id password hashing, and persistent secret management.

use argon2::{
    password_hash::{rand_core::OsRng, PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2,
};
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,
    pub exp: usize,
    pub iat: usize,
}

pub struct AuthManager {
    secret: Vec<u8>,
    password_hash: Option<String>,
}

impl AuthManager {
    /// Initialize AuthManager, reading or generating persistent secret in config path.
    pub fn new<P: AsRef<Path>>(config_dir: P) -> Self {
        let dir = config_dir.as_ref();
        let _ = fs::create_dir_all(dir);
        let secret_file = dir.join("jwt_secret.bin");

        let secret = if secret_file.exists() {
            fs::read(&secret_file).unwrap_or_else(|_| Self::generate_secret(&secret_file))
        } else {
            Self::generate_secret(&secret_file)
        };

        Self {
            secret,
            password_hash: None,
        }
    }

    fn generate_secret(file_path: &Path) -> Vec<u8> {
        use rand::RngCore;
        let mut key = vec![0u8; 32];
        rand::thread_rng().fill_bytes(&mut key);
        let _ = fs::write(file_path, &key);
        key
    }

    pub fn set_password(&mut self, password: &str) -> Result<(), String> {
        let salt = SaltString::generate(&mut OsRng);
        let argon2 = Argon2::default();
        let hash = argon2
            .hash_password(password.as_bytes(), &salt)
            .map_err(|e| format!("Password hashing failed: {}", e))?
            .to_string();

        self.password_hash = Some(hash);
        Ok(())
    }

    pub fn verify_password(&self, password: &str) -> bool {
        match &self.password_hash {
            Some(hash_str) => {
                if let Ok(parsed_hash) = PasswordHash::new(hash_str) {
                    Argon2::default()
                        .verify_password(password.as_bytes(), &parsed_hash)
                        .is_ok()
                } else {
                    false
                }
            }
            None => true, // Default to open if no password configured
        }
    }

    pub fn issue_jwt(&self, subject: &str, ttl_secs: u64) -> Result<String, String> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs() as usize;

        let claims = Claims {
            sub: subject.to_string(),
            exp: now + (ttl_secs as usize),
            iat: now,
        };

        encode(
            &Header::default(),
            &claims,
            &EncodingKey::from_secret(&self.secret),
        )
        .map_err(|e| format!("JWT encoding error: {}", e))
    }

    pub fn verify_jwt(&self, token: &str) -> Result<Claims, String> {
        let mut validation = Validation::default();
        validation.validate_exp = true;

        decode::<Claims>(
            token,
            &DecodingKey::from_secret(&self.secret),
            &validation,
        )
        .map(|data| data.claims)
        .map_err(|e| format!("Invalid JWT: {}", e))
    }
}
