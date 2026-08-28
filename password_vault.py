"""
Core password vault module.
Contains the main PasswordVault class that orchestrates all operations.
"""

import os
from datetime import datetime
from typing import List, Optional, Dict
from database import Database
from encryption import EncryptionManager
from password_generator import PasswordGenerator


class PasswordEntry:
    """
    Represents a single password entry in the vault.
    """

    def __init__(self, site: str, username: str, password: str, notes: str = "", entry_id: int = None):
        """
        Initialize a password entry.
        
        Args:
            site: Website/service name
            username: Username or email
            password: The password
            notes: Optional notes
            entry_id: Database ID (if fetched from database)
        """
        self.id = entry_id
        self.site = site
        self.username = username
        self.password = password
        self.notes = notes

    def to_dict(self) -> dict:
        """Convert entry to dictionary."""
        return {
            'id': self.id,
            'site': self.site,
            'username': self.username,
            'password': self.password,
            'notes': self.notes
        }


class PasswordVault:
    """
    Main password vault class that manages all vault operations.
    Handles authentication, encryption, and credential management.
    """

    def __init__(self, db_path: str = "vault.db"):
        """
        Initialize the password vault.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db = Database(db_path)
        self.encryption = EncryptionManager()
        self.password_generator = PasswordGenerator()
        self.master_password = None
        self.salt = None
        self.is_authenticated = False

    def initialize_vault(self, master_password: str) -> bool:
        """
        Initialize a new vault with a master password.
        
        Args:
            master_password: The master password to protect the vault
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If vault is already initialized or password is weak
        """
        if self.db.get_master_password_hash() is not None:
            raise ValueError("Vault is already initialized")
        
        if not self._validate_password(master_password):
            raise ValueError("Master password is too weak. Use at least 8 characters with mixed types.")
        
        # Derive key and save hash
        key, salt = self.encryption.derive_key_from_master_password(master_password)
        password_hash = self.encryption.hash_master_password(master_password, salt)
        
        self.db.set_master_password(password_hash, salt)
        self.master_password = master_password
        self.salt = salt
        self.is_authenticated = True
        
        return True

    def unlock_vault(self, master_password: str) -> bool:
        """
        Unlock the vault with the master password.
        
        Args:
            master_password: The master password
            
        Returns:
            True if password is correct
            
        Raises:
            ValueError: If master password is incorrect or vault not initialized
        """
        result = self.db.get_master_password_hash()
        
        if result is None:
            raise ValueError("Vault not initialized. Please set up a master password first.")
        
        stored_hash, salt = result
        
        if not self.encryption.verify_master_password(master_password, stored_hash):
            raise ValueError("Incorrect master password")
        
        self.master_password = master_password
        self.salt = salt
        self.is_authenticated = True
        
        return True

    def lock_vault(self):
        """Lock the vault by clearing authentication."""
        self.master_password = None
        self.is_authenticated = False

    def _check_authentication(self):
        """Check if vault is unlocked."""
        if not self.is_authenticated:
            raise RuntimeError("Vault is locked. Please unlock it first.")

    def _validate_password(self, password: str) -> bool:
        """
        Validate master password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            True if password is strong enough
        """
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_upper and has_lower and has_digit

    def add_credential(self, site: str, username: str, password: str, notes: str = "") -> int:
        """
        Add a new credential to the vault.
        
        Args:
            site: Website/service name
            username: Username or email
            password: The password
            notes: Optional notes
            
        Returns:
            ID of the new credential
            
        Raises:
            RuntimeError: If vault is not unlocked
            ValueError: If credential already exists or inputs invalid
        """
        self._check_authentication()
        
        if not site or not username or not password:
            raise ValueError("Site, username, and password are required")
        
        site = site.strip()
        username = username.strip()

        if not site or not username or not password.strip():
            raise ValueError("Site, username, and password are required")
        
        # Encrypt the password
        encrypted_password = self.encryption.encrypt_password(
            password, self.master_password, self.salt
        )
        
        # Add to database
        credential_id = self.db.add_credential(site, username, encrypted_password, notes)
        
        return credential_id

    def get_credential(self, credential_id: int) -> Optional[PasswordEntry]:
        """
        Retrieve a credential by ID.
        
        Args:
            credential_id: ID of the credential
            
        Returns:
            PasswordEntry or None if not found
            
        Raises:
            RuntimeError: If vault is not unlocked
        """
        self._check_authentication()
        
        cred = self.db.get_credential(credential_id)
        
        if cred:
            # Decrypt password
            decrypted_password = self.encryption.decrypt_password(
                cred['password_encrypted'], self.master_password, self.salt
            )
            
            return PasswordEntry(
                site=cred['site'],
                username=cred['username'],
                password=decrypted_password,
                notes=cred['notes'],
                entry_id=cred['id']
            )
        
        return None

    def get_all_credentials(self) -> List[PasswordEntry]:
        """
        Retrieve all credentials (without passwords decrypted).
        
        Returns:
            List of PasswordEntry objects
            
        Raises:
            RuntimeError: If vault is not unlocked
        """
        self._check_authentication()
        
        credentials = self.db.get_all_credentials()
        entries = []
        
        for cred in credentials:
            entry = PasswordEntry(
                site=cred['site'],
                username=cred['username'],
                password="[ENCRYPTED]",  # Don't decrypt all passwords for performance
                notes=cred['notes'],
                entry_id=cred['id']
            )
            entries.append(entry)
        
        return entries

    def search_credentials(self, query: str) -> List[PasswordEntry]:
        """
        Search credentials by site or username.
        
        Args:
            query: Search query
            
        Returns:
            List of matching PasswordEntry objects
            
        Raises:
            RuntimeError: If vault is not unlocked
        """
        self._check_authentication()
        
        credentials = self.db.search_credentials(query)
        entries = []
        
        for cred in credentials:
            entry = PasswordEntry(
                site=cred['site'],
                username=cred['username'],
                password="[ENCRYPTED]",
                notes=cred['notes'],
                entry_id=cred['id']
            )
            entries.append(entry)
        
        return entries

    def update_credential(self, credential_id: int, site: str = None,
                         username: str = None, password: str = None,
                         notes: str = None) -> bool:
        """
        Update an existing credential.
        
        Args:
            credential_id: ID of the credential to update
            site: New site name (optional)
            username: New username (optional)
            password: New password (optional)
            notes: New notes (optional)
            
        Returns:
            True if successful
            
        Raises:
            RuntimeError: If vault is not unlocked
        """
        self._check_authentication()

        if site is not None:
            site = site.strip()
            if not site:
                raise ValueError("Site cannot be empty")
        if username is not None:
            username = username.strip()
            if not username:
                raise ValueError("Username cannot be empty")
        if password is not None and not password.strip():
            raise ValueError("Password cannot be empty")
        
        # Encrypt password if provided
        encrypted_password = None
        if password is not None:
            encrypted_password = self.encryption.encrypt_password(
                password, self.master_password, self.salt
            )
        
        return self.db.update_credential(
            credential_id, site, username, encrypted_password, notes
        )

    def delete_credential(self, credential_id: int) -> bool:
        """
        Delete a credential from the vault.
        
        Args:
            credential_id: ID of the credential to delete
            
        Returns:
            True if successful
            
        Raises:
            RuntimeError: If vault is not unlocked
        """
        self._check_authentication()
        return self.db.delete_credential(credential_id)

    def generate_password(self, length: int = 16, use_uppercase: bool = True,
                         use_digits: bool = True, use_special: bool = True) -> str:
        """
        Generate a strong random password.
        
        Args:
            length: Password length
            use_uppercase: Include uppercase letters
            use_digits: Include digits
            use_special: Include special characters
            
        Returns:
            Generated password
        """
        return self.password_generator.generate(
            length, use_uppercase, use_digits, use_special
        )

    def evaluate_password_strength(self, password: str) -> tuple:
        """
        Evaluate the strength of a password.
        
        Args:
            password: Password to evaluate
            
        Returns:
            Tuple of (score, level, feedback)
        """
        return self.password_generator.evaluate_strength(password)

    def export_encrypted_backup(self, export_path: str) -> bool:
        """
        Export all credentials to an encrypted backup file.
        
        Args:
            export_path: Path to save the backup file
            
        Returns:
            True if successful
            
        Raises:
            RuntimeError: If vault is not unlocked
        """
        self._check_authentication()
        
        try:
            credentials = self.db.get_all_credentials()
            
            # Create backup content
            backup_content = "Password Vault Backup\n"
            backup_content += f"Created: {datetime.now().isoformat()}\n"
            backup_content += "=" * 50 + "\n\n"
            
            for cred in credentials:
                # Decrypt password for backup
                decrypted = self.encryption.decrypt_password(
                    cred['password_encrypted'], self.master_password, self.salt
                )
                
                backup_content += f"Site: {cred['site']}\n"
                backup_content += f"Username: {cred['username']}\n"
                backup_content += f"Password: {decrypted}\n"
                if cred['notes']:
                    backup_content += f"Notes: {cred['notes']}\n"
                backup_content += "-" * 50 + "\n\n"
            
            # Encrypt the entire backup
            encrypted_backup = self.encryption.encrypt_password(
                backup_content, self.master_password, self.salt
            )
            
            # Write to file
            with open(export_path, 'w') as f:
                f.write(encrypted_backup)
            
            # Log backup
            file_size = os.path.getsize(export_path)
            self.db.log_backup(export_path, file_size)
            
            return True
        except Exception as e:
            raise RuntimeError(f"Backup export failed: {str(e)}")

    def close(self):
        """Close the vault and database connection."""
        self.lock_vault()
        self.db.close()

    def __del__(self):
        """Ensure vault is closed when object is destroyed."""
        self.close()
