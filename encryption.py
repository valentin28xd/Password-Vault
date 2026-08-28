"""
Encryption module for secure password handling.
Uses Fernet (symmetric encryption) from the cryptography library.
"""

import os
import hashlib
import hmac
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64


class EncryptionManager:
    """
    Handles all encryption and decryption operations for the password vault.
    Uses Fernet for symmetric encryption with PBKDF2 key derivation.
    """

    def __init__(self):
        """Initialize the encryption manager."""
        self.backend = default_backend()
        self.hash_iterations = 100000

    def derive_key_from_master_password(self, master_password: str, salt: bytes = None) -> tuple:
        """
        Derive an encryption key from the master password using PBKDF2.
        
        Args:
            master_password: The master password entered by the user
            salt: Optional salt. If None, generates a new one
            
        Returns:
            Tuple of (encryption_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        # Use PBKDF2 with SHA256 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.hash_iterations,
            backend=self.backend
        )
        
        # Derive key from master password
        key = kdf.derive(master_password.encode())
        
        # Encode key for Fernet (base64 format required)
        encoded_key = base64.urlsafe_b64encode(key)
        
        return encoded_key, salt

    def encrypt_password(self, password: str, master_password: str, salt: bytes) -> str:
        """
        Encrypt a password using the master password.
        
        Args:
            password: The password to encrypt
            master_password: The master password
            salt: The salt used for key derivation
            
        Returns:
            Encrypted password as base64 string
        """
        try:
            key, _ = self.derive_key_from_master_password(master_password, salt)
            fernet = Fernet(key)
            encrypted = fernet.encrypt(password.encode())
            return encrypted.decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")

    def decrypt_password(self, encrypted_password: str, master_password: str, salt: bytes) -> str:
        """
        Decrypt a password using the master password.
        
        Args:
            encrypted_password: The encrypted password
            master_password: The master password
            salt: The salt used for key derivation
            
        Returns:
            Decrypted password
        """
        try:
            key, _ = self.derive_key_from_master_password(master_password, salt)
            fernet = Fernet(key)
            decrypted = fernet.decrypt(encrypted_password.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def hash_master_password(self, master_password: str, salt: bytes = None) -> str:
        """
        Hash the master password for verification (stored in database).
        
        Args:
            master_password: The master password to hash
            
        Returns:
            Versioned PBKDF2-HMAC hash when a salt is supplied. The unsalted
            SHA-256 form is retained for compatibility with direct callers.
        """
        if salt is not None:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self.hash_iterations,
                backend=self.backend
            )
            digest = base64.urlsafe_b64encode(kdf.derive(master_password.encode())).decode()
            encoded_salt = base64.urlsafe_b64encode(salt).decode()
            return f"pbkdf2_sha256${self.hash_iterations}${encoded_salt}${digest}"

        return hashlib.sha256(master_password.encode()).hexdigest()

    def verify_master_password(self, master_password: str, stored_hash: str) -> bool:
        """
        Verify the master password against the stored hash.
        
        Args:
            master_password: The master password to verify
            stored_hash: The stored hash from database
            
        Returns:
            True if password matches, False otherwise
        """
        if stored_hash.startswith("pbkdf2_sha256$"):
            try:
                _, iterations, encoded_salt, encoded_digest = stored_hash.split("$", 3)
                salt = base64.urlsafe_b64decode(encoded_salt.encode())
                expected_digest = base64.urlsafe_b64decode(encoded_digest.encode())
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=len(expected_digest),
                    salt=salt,
                    iterations=int(iterations),
                    backend=self.backend
                )
                actual_digest = kdf.derive(master_password.encode())
                return hmac.compare_digest(actual_digest, expected_digest)
            except (ValueError, TypeError):
                return False

        return hmac.compare_digest(self.hash_master_password(master_password), stored_hash)
