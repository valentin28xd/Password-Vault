"""
Unit tests and integration tests for the password vault.
Tests all major components and functionality.
"""

import unittest
import os
import tempfile
from password_vault import PasswordVault, PasswordEntry
from database import Database
from encryption import EncryptionManager
from password_generator import PasswordGenerator


class TestEncryptionManager(unittest.TestCase):
    """Test the encryption manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.encryption = EncryptionManager()
        self.master_password = "MySecurePassword123"

    def test_derive_key_from_master_password(self):
        """Test key derivation."""
        key1, salt1 = self.encryption.derive_key_from_master_password(self.master_password)
        key2, salt2 = self.encryption.derive_key_from_master_password(self.master_password, salt1)
        
        # Same salt should produce same key
        self.assertEqual(key1, key2)
        self.assertEqual(salt1, salt2)

    def test_encrypt_decrypt_password(self):
        """Test password encryption and decryption."""
        password = "MySecurePassword"
        key, salt = self.encryption.derive_key_from_master_password(self.master_password)
        
        encrypted = self.encryption.encrypt_password(password, self.master_password, salt)
        decrypted = self.encryption.decrypt_password(encrypted, self.master_password, salt)
        
        self.assertEqual(password, decrypted)

    def test_wrong_password_decryption(self):
        """Test that wrong password fails decryption."""
        password = "MySecurePassword"
        key, salt = self.encryption.derive_key_from_master_password(self.master_password)
        
        encrypted = self.encryption.encrypt_password(password, self.master_password, salt)
        
        with self.assertRaises(ValueError):
            self.encryption.decrypt_password(encrypted, "WrongPassword", salt)

    def test_hash_master_password(self):
        """Test master password hashing."""
        hash1 = self.encryption.hash_master_password(self.master_password)
        hash2 = self.encryption.hash_master_password(self.master_password)
        
        # Same password should produce same hash
        self.assertEqual(hash1, hash2)

    def test_verify_master_password(self):
        """Test master password verification."""
        hash_value = self.encryption.hash_master_password(self.master_password)
        
        # Correct password
        self.assertTrue(self.encryption.verify_master_password(self.master_password, hash_value))
        
        # Wrong password
        self.assertFalse(self.encryption.verify_master_password("WrongPassword", hash_value))

    def test_salted_master_password_hash(self):
        """Test the salted master password hash used by vaults."""
        _, salt = self.encryption.derive_key_from_master_password(self.master_password)
        hash_value = self.encryption.hash_master_password(self.master_password, salt)

        self.assertTrue(hash_value.startswith("pbkdf2_sha256$"))
        self.assertTrue(self.encryption.verify_master_password(self.master_password, hash_value))
        self.assertFalse(self.encryption.verify_master_password("WrongPassword", hash_value))


class TestPasswordGenerator(unittest.TestCase):
    """Test the password generator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = PasswordGenerator()

    def test_generate_password_default(self):
        """Test default password generation."""
        password = self.generator.generate()
        
        # Should be 16 characters
        self.assertEqual(len(password), 16)

    def test_generate_password_custom_length(self):
        """Test password generation with custom length."""
        for length in [8, 12, 20, 32]:
            password = self.generator.generate(length=length)
            self.assertEqual(len(password), length)

    def test_password_contains_required_chars(self):
        """Test that generated password contains required character types."""
        password = self.generator.generate(
            use_uppercase=True,
            use_digits=True,
            use_special=True
        )
        
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()" for c in password)
        
        self.assertTrue(has_upper or has_digit or has_special)

    def test_password_strength_evaluation(self):
        """Test password strength evaluation."""
        weak_password = "pass"
        strong_password = "MySecurePass123!@#"
        
        weak_score, weak_level, _ = self.generator.evaluate_strength(weak_password)
        strong_score, strong_level, _ = self.generator.evaluate_strength(strong_password)
        
        # Strong password should have higher score
        self.assertGreater(strong_score, weak_score)

    def test_generate_multiple_passwords(self):
        """Test generating multiple passwords."""
        passwords = self.generator.generate_multiple(count=5)
        
        self.assertEqual(len(passwords), 5)
        # All should be unique
        self.assertEqual(len(set(passwords)), 5)

    def test_generator_respects_character_options(self):
        """Test that selected character categories are represented."""
        password = self.generator.generate(
            length=12, use_lowercase=False, use_uppercase=True,
            use_digits=True, use_special=False
        )

        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(all(not c.islower() for c in password))

    def test_generator_requires_a_character_type(self):
        """Test that disabling every character category is rejected."""
        with self.assertRaises(ValueError):
            self.generator.generate(
                use_lowercase=False, use_uppercase=False,
                use_digits=False, use_special=False
            )


class TestDatabase(unittest.TestCase):
    """Test the database operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_set_master_password(self):
        """Test setting master password."""
        password_hash = "hash123"
        salt = b"salt"
        
        result = self.db.set_master_password(password_hash, salt)
        self.assertTrue(result)
        
        stored = self.db.get_master_password_hash()
        self.assertEqual(stored[0], password_hash)
        self.assertEqual(stored[1], salt)

    def test_add_credential(self):
        """Test adding a credential."""
        cred_id = self.db.add_credential("gmail.com", "user@gmail.com", "encrypted_pass", "Email account")
        
        self.assertIsNotNone(cred_id)
        
        cred = self.db.get_credential(cred_id)
        self.assertEqual(cred['site'], "gmail.com")
        self.assertEqual(cred['username'], "user@gmail.com")

    def test_duplicate_credential(self):
        """Test that duplicate credentials are prevented."""
        self.db.add_credential("gmail.com", "user@gmail.com", "pass1")
        
        with self.assertRaises(ValueError):
            self.db.add_credential("gmail.com", "user@gmail.com", "pass2")

    def test_get_all_credentials(self):
        """Test retrieving all credentials."""
        self.db.add_credential("site1.com", "user1", "pass1")
        self.db.add_credential("site2.com", "user2", "pass2")
        self.db.add_credential("site3.com", "user3", "pass3")
        
        credentials = self.db.get_all_credentials()
        self.assertEqual(len(credentials), 3)

    def test_search_credentials(self):
        """Test searching credentials."""
        self.db.add_credential("gmail.com", "user1@gmail.com", "pass1")
        self.db.add_credential("github.com", "user2", "pass2")
        self.db.add_credential("google.com", "user3", "pass3")
        
        # Search by site
        results = self.db.search_credentials("gmail")
        self.assertEqual(len(results), 1)
        
        # Search by username
        results = self.db.search_credentials("user2")
        self.assertEqual(len(results), 1)

    def test_update_credential(self):
        """Test updating a credential."""
        cred_id = self.db.add_credential("site.com", "user", "pass", "notes")
        
        self.db.update_credential(cred_id, site="newsite.com", username="newuser")
        
        cred = self.db.get_credential(cred_id)
        self.assertEqual(cred['site'], "newsite.com")
        self.assertEqual(cred['username'], "newuser")

    def test_delete_credential(self):
        """Test deleting a credential."""
        cred_id = self.db.add_credential("site.com", "user", "pass")
        
        result = self.db.delete_credential(cred_id)
        self.assertTrue(result)
        
        cred = self.db.get_credential(cred_id)
        self.assertIsNone(cred)


class TestPasswordVault(unittest.TestCase):
    """Test the main password vault."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.vault = PasswordVault(self.temp_db.name)
        self.master_password = "TestPassword123"

    def tearDown(self):
        """Clean up test fixtures."""
        self.vault.close()
        os.unlink(self.temp_db.name)

    def test_initialize_vault(self):
        """Test vault initialization."""
        result = self.vault.initialize_vault(self.master_password)
        self.assertTrue(result)
        self.assertTrue(self.vault.is_authenticated)

    def test_weak_master_password(self):
        """Test that weak master passwords are rejected."""
        with self.assertRaises(ValueError):
            self.vault.initialize_vault("weak")

    def test_unlock_vault(self):
        """Test unlocking the vault."""
        self.vault.initialize_vault(self.master_password)
        self.vault.lock_vault()
        self.assertFalse(self.vault.is_authenticated)
        
        result = self.vault.unlock_vault(self.master_password)
        self.assertTrue(result)
        self.assertTrue(self.vault.is_authenticated)

    def test_wrong_master_password(self):
        """Test that wrong master password is rejected."""
        self.vault.initialize_vault(self.master_password)
        self.vault.lock_vault()
        
        with self.assertRaises(ValueError):
            self.vault.unlock_vault("WrongPassword123")

    def test_add_credential(self):
        """Test adding a credential."""
        self.vault.initialize_vault(self.master_password)
        
        cred_id = self.vault.add_credential("gmail.com", "user@gmail.com", "mypassword")
        self.assertIsNotNone(cred_id)

    def test_get_credential(self):
        """Test retrieving a credential."""
        self.vault.initialize_vault(self.master_password)
        
        cred_id = self.vault.add_credential("gmail.com", "user@gmail.com", "mypassword", "My email")
        
        cred = self.vault.get_credential(cred_id)
        self.assertEqual(cred.site, "gmail.com")
        self.assertEqual(cred.username, "user@gmail.com")
        self.assertEqual(cred.password, "mypassword")
        self.assertEqual(cred.notes, "My email")

    def test_operation_without_authentication(self):
        """Test that operations fail without authentication."""
        with self.assertRaises(RuntimeError):
            self.vault.add_credential("site.com", "user", "pass")

    def test_update_credential(self):
        """Test updating a credential."""
        self.vault.initialize_vault(self.master_password)
        
        cred_id = self.vault.add_credential("gmail.com", "user@gmail.com", "password1")
        
        self.vault.update_credential(cred_id, password="password2")
        
        cred = self.vault.get_credential(cred_id)
        self.assertEqual(cred.password, "password2")

    def test_update_rejects_blank_required_fields(self):
        """Test that updates cannot clear required credential fields."""
        self.vault.initialize_vault(self.master_password)
        cred_id = self.vault.add_credential("site.com", "user", "password")

        with self.assertRaises(ValueError):
            self.vault.update_credential(cred_id, site=" ")
        with self.assertRaises(ValueError):
            self.vault.update_credential(cred_id, username="")
        with self.assertRaises(ValueError):
            self.vault.update_credential(cred_id, password="\t")

    def test_delete_credential(self):
        """Test deleting a credential."""
        self.vault.initialize_vault(self.master_password)
        
        cred_id = self.vault.add_credential("gmail.com", "user@gmail.com", "password")
        
        result = self.vault.delete_credential(cred_id)
        self.assertTrue(result)
        
        cred = self.vault.get_credential(cred_id)
        self.assertIsNone(cred)

    def test_export_backup(self):
        """Test exporting a backup."""
        self.vault.initialize_vault(self.master_password)
        
        self.vault.add_credential("gmail.com", "user@gmail.com", "password1")
        self.vault.add_credential("github.com", "user", "password2")
        
        temp_backup = tempfile.NamedTemporaryFile(delete=False, suffix='.vault')
        temp_backup.close()
        
        try:
            result = self.vault.export_encrypted_backup(temp_backup.name)
            self.assertTrue(result)
            
            # Verify backup file exists and has content
            with open(temp_backup.name, 'r') as f:
                content = f.read()
                self.assertTrue(len(content) > 0)
        finally:
            os.unlink(temp_backup.name)


class TestIntegration(unittest.TestCase):
    """Integration tests simulating real-world usage."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.vault = PasswordVault(self.temp_db.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.vault.close()
        os.unlink(self.temp_db.name)

    def test_full_workflow(self):
        """Test a complete workflow from setup to backup."""
        master_password = "MyVaultPassword123"
        
        # Initialize vault
        self.vault.initialize_vault(master_password)
        
        # Add multiple credentials
        gmail_id = self.vault.add_credential("gmail.com", "user@gmail.com", "GmailPass123!", "Personal email")
        github_id = self.vault.add_credential("github.com", "username", "GitHubPass456!", "Code repository")
        bank_id = self.vault.add_credential("bank.com", "account123", "BankPass789!@", "Bank account")
        
        # Verify credentials can be retrieved
        self.assertIsNotNone(self.vault.get_credential(gmail_id))
        self.assertIsNotNone(self.vault.get_credential(github_id))
        self.assertIsNotNone(self.vault.get_credential(bank_id))
        
        # Search credentials
        results = self.vault.search_credentials("gmail")
        self.assertEqual(len(results), 1)
        
        # Update a credential
        self.vault.update_credential(github_id, username="newusername")
        updated = self.vault.get_credential(github_id)
        self.assertEqual(updated.username, "newusername")
        
        # Delete a credential
        self.vault.delete_credential(bank_id)
        self.assertIsNone(self.vault.get_credential(bank_id))
        
        # Lock vault
        self.vault.lock_vault()
        self.assertFalse(self.vault.is_authenticated)
        
        # Unlock vault again
        self.vault.unlock_vault(master_password)
        self.assertTrue(self.vault.is_authenticated)
        
        # Verify data persists
        self.assertIsNotNone(self.vault.get_credential(gmail_id))
        self.assertIsNotNone(self.vault.get_credential(github_id))


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEncryptionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordVault))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
