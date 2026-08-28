# Development Guide

This document provides detailed information for developers working with the Password Vault codebase.

## Project Structure

```
password_vault/
├── encryption.py           # Encryption/decryption module
├── database.py            # Database abstraction layer
├── password_vault.py      # Core vault business logic
├── password_generator.py  # Password generation utilities
├── gui.py                 # Tkinter GUI implementation
├── cli.py                 # Command-line interface
├── main.py                # Entry point
├── test_vault.py          # Test suite
├── requirements.txt       # Dependencies
├── README.md              # User documentation
├── DEVELOPMENT.md         # This file
└── vault.db              # SQLite database (created at runtime)
```

## Class Hierarchy & Design

### 1. EncryptionManager (encryption.py)

Handles all cryptographic operations using Fernet and PBKDF2.

**Key Methods:**
- `derive_key_from_master_password()` - Generate encryption key from password
- `encrypt_password()` - Encrypt a password
- `decrypt_password()` - Decrypt a password
- `hash_master_password()` - Hash master password for storage
- `verify_master_password()` - Verify master password

**Security Design:**
- Uses PBKDF2 with SHA256 for key derivation
- 100,000 iterations to resist brute-force attacks
- Random salt generation for each vault
- Fernet provides authentication (HMAC) + encryption

### 2. Database (database.py)

SQLite abstraction layer for all database operations.

**Key Methods:**
- `set_master_password()` - Store master password hash
- `add_credential()` - Insert credential
- `get_credential()` - Fetch by ID
- `get_all_credentials()` - Fetch all
- `search_credentials()` - Search by site/username
- `update_credential()` - Modify existing credential
- `delete_credential()` - Remove credential

**Error Handling:**
- All methods catch SQLite exceptions
- Raise custom exceptions with meaningful messages
- Ensure ACID compliance

### 3. PasswordGenerator (password_generator.py)

Generates strong passwords and evaluates password strength.

**Key Methods:**
- `generate()` - Generate random password
- `generate_multiple()` - Generate batch of passwords
- `evaluate_strength()` - Score password strength 0-100

**Strength Criteria:**
- Length (8, 12, 16+ characters)
- Character types (lowercase, uppercase, digits, special)
- Common patterns detection
- Returns feedback for improvement

### 4. PasswordVault (password_vault.py)

Core vault business logic orchestrating all operations.

**Key Classes:**
- `PasswordEntry` - Represents single credential
- `PasswordVault` - Main vault manager

**Key Methods:**
- `initialize_vault()` - Setup new vault
- `unlock_vault()` - Authenticate
- `lock_vault()` - Clear authentication
- `add_credential()` - Add password entry
- `get_credential()` - Retrieve entry
- `search_credentials()` - Find entries
- `update_credential()` - Modify entry
- `delete_credential()` - Remove entry
- `export_encrypted_backup()` - Backup all credentials

**Authentication Flow:**
```
1. initialize_vault(master_password)
   → derive key from password
   → hash password
   → store in database
   → set is_authenticated = True

2. lock_vault()
   → clear master_password
   → clear salt
   → set is_authenticated = False

3. unlock_vault(master_password)
   → retrieve hash and salt
   → verify against master_password
   → set is_authenticated = True
```

### 5. PasswordVaultGUI (gui.py)

Tkinter-based graphical interface.

**Screen Components:**
- `create_login_screen()` - Initial login/setup
- `create_setup_screen()` - New vault creation
- `create_login_form()` - Existing vault login
- `create_main_screen()` - Main vault interface
- `display_credentials()` - Table of credentials

**Dialog Windows:**
- Add credential dialog
- Edit credential dialog
- View credential details
- Password generator with strength meter

**Event Handling:**
- Double-click to view credential details
- Search filtering
- Context menus for actions
- Clipboard operations

### 6. PasswordVaultCLI (cli.py)

Command-line interface with interactive menu system.

**Menu Options:**
1. List all credentials
2. View credential
3. Add new credential
4. Edit credential
5. Delete credential
6. Search credentials
7. Generate password
8. Export backup
9. Lock vault
0. Exit

**Features:**
- Table formatting with tabulate
- Password masking with getpass
- Input validation
- User-friendly error messages

## Development Workflow

### Adding a New Feature

1. **Write Tests First** (TDD approach)
   ```python
   # In test_vault.py
   def test_new_feature(self):
       # Test the feature
       pass
   ```

2. **Implement Feature**
   ```python
   # In appropriate module
   def new_feature(self):
       """Docstring explaining the feature."""
       # Implementation
       pass
   ```

3. **Update Documentation**
   - Add to README.md if user-facing
   - Add to DEVELOPMENT.md if developer-facing
   - Update docstrings

4. **Test Thoroughly**
   ```bash
   python test_vault.py
   python main.py --test
   ```

### Adding Database Operations

1. Add method to `Database` class
2. Follow naming convention: verb_noun (e.g., `add_credential`)
3. Handle SQLite exceptions
4. Use row_factory for dict-like access

### Adding Encryption Operations

1. Add method to `EncryptionManager`
2. Document cryptographic details
3. Test with various inputs
4. Handle exceptions with meaningful messages

### Adding GUI Elements

1. Use ttk widgets for modern look
2. Follow callback pattern: `def on_action():`
3. Use `messagebox` for user feedback
4. Clean up child widgets before updates
5. Use lambda for callbacks with parameters

## Code Style

Follow PEP 8 conventions:

```python
# Imports at top
from module import Class

# Class definition
class MyClass:
    """Class docstring."""
    
    def __init__(self):
        """Constructor docstring."""
        self.attribute = value
    
    def method(self, param):
        """Method docstring.
        
        Args:
            param: Parameter description
            
        Returns:
            Description of return value
            
        Raises:
            ExceptionType: When this exception occurs
        """
        return result

# Function definition
def my_function(param):
    """Function docstring."""
    return result

# Spacing
x = 1  # Space around operators
list = [1, 2, 3]  # Space after commas
```

## Error Handling Strategy

### Exception Hierarchy

```
Exception
├── ValueError (invalid input)
├── RuntimeError (operational error)
├── KeyError (missing data)
└── SQLite3.Error (database error)
```

### Best Practices

1. **Be Specific**
   ```python
   # Good
   if not password:
       raise ValueError("Password is required")
   
   # Avoid
   raise Exception("Error")
   ```

2. **Provide Context**
   ```python
   try:
       decrypt_password()
   except CryptographyError as e:
       raise ValueError(f"Decryption failed: {str(e)}")
   ```

3. **Clean Up Resources**
   ```python
   try:
       # Do something
   finally:
       self.close()
   ```

## Testing Strategy

### Test Types

1. **Unit Tests** - Individual functions/methods
2. **Integration Tests** - Multiple components together
3. **Encryption Tests** - Cryptography verification
4. **Database Tests** - CRUD operations
5. **GUI Tests** - User interactions (manual)

### Running Tests

```bash
# Run all tests
python test_vault.py

# Run specific test
python -m unittest test_vault.TestEncryptionManager

# Run with verbose output
python -m unittest test_vault -v
```

### Writing Tests

```python
class TestMyFeature(unittest.TestCase):
    def setUp(self):
        """Called before each test."""
        self.fixture = setup()
    
    def tearDown(self):
        """Called after each test."""
        cleanup(self.fixture)
    
    def test_valid_case(self):
        """Test successful operation."""
        result = operation()
        self.assertEqual(result, expected)
    
    def test_error_case(self):
        """Test error handling."""
        with self.assertRaises(ValueError):
            operation(invalid_input)
```

## Performance Considerations

### Optimization Areas

1. **Database Queries**
   - Use indexes on frequently searched columns
   - Batch operations when possible
   - Close connections properly

2. **Encryption**
   - PBKDF2 iterations (100,000) = ~1-2 sec delay
   - Intentional for security (brute-force resistance)
   - Cannot be reduced without security compromise

3. **GUI Rendering**
   - Don't decrypt all passwords at once
   - Use threading for long operations
   - Lazy load data when possible

4. **Memory**
   - Clear sensitive data (passwords) when done
   - Use generators for large datasets
   - Delete temporary variables

## Security Considerations

### Sensitive Data Handling

1. **Master Password**
   - Never log or print
   - Only store hash in database
   - Clear from memory after use

2. **Encrypted Passwords**
   - Never decrypt to disk
   - Only decrypt when needed
   - Clear after use

3. **Salt and Keys**
   - Never expose salt
   - Never log encryption keys
   - Generate new salt for each vault

### Code Review Checklist

- [ ] No passwords in logs/comments
- [ ] No hardcoded credentials
- [ ] Proper exception handling
- [ ] Input validation on all user input
- [ ] No SQL injection vulnerabilities
- [ ] Proper file permissions on database
- [ ] Clean up temporary files

## Deployment

### Packaging

```bash
# Create distribution
python setup.py sdist bdist_wheel

# Install locally
pip install -e .
```

### Bundling

```bash
# Create standalone executable
pip install pyinstaller
pyinstaller --onefile main.py
```

### Distribution

1. Create GitHub release
2. Add changelog
3. Include checksums
4. Sign with GPG if possible

## Troubleshooting Development

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Database Locked

```python
# SQLite timeout issue
conn.execute("PRAGMA busy_timeout = 5000")
```

### GUI Not Showing

```bash
# Linux tkinter issue
sudo apt install python3-tk

# Update tkinter
pip install --upgrade tk
```

### Encryption Errors

- Check Python version (3.8+)
- Verify cryptography library installed
- Test with simple operations first

## Future Enhancements

### Short Term
- [ ] Auto-lock timer configuration
- [ ] Password history
- [ ] Import from CSV/JSON
- [ ] Keyboard shortcuts

### Medium Term
- [ ] Database encryption at rest
- [ ] Multiple vaults
- [ ] Sharing credentials safely
- [ ] Two-factor authentication

### Long Term
- [ ] Web interface
- [ ] Mobile apps (iOS/Android)
- [ ] Cloud synchronization
- [ ] Biometric authentication
- [ ] Machine learning for security analysis

## Contributing Guidelines

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### PR Requirements
- Tests passing
- Code style compliant
- Documentation updated
- No security issues
- Clear commit messages

## Resources

### Security
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/)
- [Cryptography.io Documentation](https://cryptography.io/)
- [SQLite Security](https://www.sqlite.org/security.html)

### Python
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

### GUI Development
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [Tkinter Best Practices](https://tkdocs.com/tutorial/)

---

**Last Updated**: 2024
**Maintainer**: Development Team
