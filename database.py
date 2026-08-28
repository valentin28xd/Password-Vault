"""
Database module for managing SQLite operations.
Handles schema creation and credential storage/retrieval.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple
import base64


class Database:
    """
    SQLite database handler for the password vault.
    Manages all database operations with proper error handling.
    """

    def __init__(self, db_path: str = "vault.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._initialize_database()

    def _initialize_database(self):
        """Create database file if it doesn't exist and initialize schema."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self._create_schema()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database initialization failed: {str(e)}")

    def _create_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.connection.cursor()
        
        # Master password table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_password (
                id INTEGER PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Credentials table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                password_encrypted TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(site, username)
            )
        """)
        
        # Backup history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_path TEXT NOT NULL,
                backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER
            )
        """)
        
        self.connection.commit()

    def set_master_password(self, password_hash: str, salt: bytes) -> bool:
        """
        Set or update the master password hash.
        
        Args:
            password_hash: SHA256 hash of the master password
            salt: Salt used for key derivation
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM master_password")
            cursor.execute(
                "INSERT INTO master_password (password_hash, salt) VALUES (?, ?)",
                (password_hash, salt)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to set master password: {str(e)}")

    def get_master_password_hash(self) -> Optional[Tuple[str, bytes]]:
        """
        Retrieve the stored master password hash and salt.
        
        Returns:
            Tuple of (password_hash, salt) or None if not set
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT password_hash, salt FROM master_password")
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve master password: {str(e)}")

    def add_credential(self, site: str, username: str, password_encrypted: str, notes: str = "") -> int:
        """
        Add a new credential to the vault.
        
        Args:
            site: Website/service name
            username: Username or email
            password_encrypted: Encrypted password
            notes: Optional notes about the credential
            
        Returns:
            ID of the inserted credential
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """INSERT INTO credentials (site, username, password_encrypted, notes)
                   VALUES (?, ?, ?, ?)""",
                (site, username, password_encrypted, notes)
            )
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Credential for {site} with username {username} already exists")
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to add credential: {str(e)}")

    def get_credential(self, credential_id: int) -> Optional[dict]:
        """
        Retrieve a specific credential by ID.
        
        Args:
            credential_id: ID of the credential
            
        Returns:
            Dictionary with credential data or None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM credentials WHERE id = ?", (credential_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve credential: {str(e)}")

    def get_all_credentials(self) -> List[dict]:
        """
        Retrieve all credentials from the vault.
        
        Returns:
            List of credential dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM credentials ORDER BY site ASC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve credentials: {str(e)}")

    def search_credentials(self, query: str) -> List[dict]:
        """
        Search credentials by site or username.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching credential dictionaries
        """
        try:
            cursor = self.connection.cursor()
            search_term = f"%{query}%"
            cursor.execute(
                """SELECT * FROM credentials 
                   WHERE site LIKE ? OR username LIKE ? 
                   ORDER BY site ASC""",
                (search_term, search_term)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to search credentials: {str(e)}")

    def update_credential(self, credential_id: int, site: str = None, username: str = None,
                         password_encrypted: str = None, notes: str = None) -> bool:
        """
        Update an existing credential.
        
        Args:
            credential_id: ID of the credential to update
            site: Updated site name (optional)
            username: Updated username (optional)
            password_encrypted: Updated encrypted password (optional)
            notes: Updated notes (optional)
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if site is not None:
                updates.append("site = ?")
                params.append(site)
            if username is not None:
                updates.append("username = ?")
                params.append(username)
            if password_encrypted is not None:
                updates.append("password_encrypted = ?")
                params.append(password_encrypted)
            if notes is not None:
                updates.append("notes = ?")
                params.append(notes)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(credential_id)
            
            query = f"UPDATE credentials SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to update credential: {str(e)}")

    def delete_credential(self, credential_id: int) -> bool:
        """
        Delete a credential from the vault.
        
        Args:
            credential_id: ID of the credential to delete
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM credentials WHERE id = ?", (credential_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to delete credential: {str(e)}")

    def log_backup(self, backup_path: str, file_size: int) -> bool:
        """
        Log a backup operation.
        
        Args:
            backup_path: Path to the backup file
            file_size: Size of the backup file in bytes
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO backup_history (backup_path, file_size) VALUES (?, ?)",
                (backup_path, file_size)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to log backup: {str(e)}")

    def get_backup_history(self, limit: int = 10) -> List[dict]:
        """
        Retrieve backup history.
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of backup history dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM backup_history ORDER BY backup_date DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve backup history: {str(e)}")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()

    def __del__(self):
        """Ensure database is closed when object is destroyed."""
        self.close()
