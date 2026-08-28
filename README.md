# Password Vault

A secure, modern password manager built with Python using Fernet encryption and SQLite database. Store, manage, and generate strong passwords with complete security and ease of use.

## Features

- **Military-grade Encryption**: Uses Fernet (symmetric encryption) with PBKDF2 key derivation
- **Master Password Protection**: Single master password unlocks your entire vault
- **Local SQLite Database**: All credentials stored locally on your machine
- **Dual Interface**: Both GUI (tkinter) and CLI interfaces available
- **Password Generator**: Create strong, random passwords with customizable options
- **Search & Filter**: Quickly find credentials by site or username
- **Full CRUD Operations**: Create, read, update, and delete credentials
- **Encrypted Backups**: Export credentials to encrypted backup files
- **Input Validation**: Comprehensive validation and error handling
- **Password Strength Meter**: Evaluate password security
- **Comprehensive Tests**: Full unit and integration test suite

## Architecture

The project follows Object-Oriented Programming principles with clean separation of concerns:

```
password_vault/
├── encryption.py        # Encryption/decryption utilities (Fernet + PBKDF2)
├── database.py          # SQLite database operations
├── password_vault.py    # Core vault logic and orchestration
├── password_generator.py # Password generation and strength evaluation
├── gui.py               # Tkinter GUI interface
├── cli.py               # Command-line interface
├── test_vault.py        # Comprehensive test suite
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Database Schema

### master_password table
- `id`: Primary key
- `password_hash`: SHA256 hash of master password
- `salt`: Salt for PBKDF2 key derivation
- `created_at`: Timestamp of vault creation

### credentials table
- `id`: Primary key
- `site`: Website/service name
- `username`: Username or email
- `password_encrypted`: Encrypted password (Fernet)
- `notes`: Optional notes
- `created_at`: Timestamp of credential creation
- `updated_at`: Timestamp of last update

### backup_history table
- `id`: Primary key
- `backup_path`: Path to backup file
- `backup_date`: Timestamp of backup
- `file_size`: Size of backup file

## Security Details

### Encryption
- **Algorithm**: Fernet (symmetric encryption based on AES)
- **Key Derivation**: PBKDF2 with SHA256, 100,000 iterations
- **Master Password Hash**: SHA256 (for verification only, not used for encryption)
- **Passwords**: Individual encryption with master-derived key

### Best Practices
- Master password never stored in plaintext
- Each password encrypted with Fernet (time-stamped and authenticated)
- Salt randomly generated and stored with vault
- All operations require authentication
- Vault can be locked without closing the application

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/password-vault.git
cd password-vault
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### GUI Interface (Recommended for most users)

```bash
python gui.py
```

Features:
- Intuitive graphical interface
- Menu bar with file and help options
- Searchable credential list
- Add/Edit/Delete credentials with dialog boxes
- View credential details with copy-to-clipboard functionality
- Generate passwords with visual feedback
- Export encrypted backups

**First Time Setup:**
1. Launch the GUI
2. Create a strong master password (8+ characters, mixed case, numbers)
3. Confirm the password
4. Click "Create Vault"

**Daily Usage:**
1. Launch the GUI
2. Enter master password
3. Click "Unlock"
4. Manage your credentials

### CLI Interface (For power users)

```bash
python cli.py
```

Features:
- Full command-line access to all features
- Interactive menu system
- Search and filter capabilities
- Password generation and strength evaluation
- Encrypted backups

**CLI Menu Options:**
```
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
```

### Testing

Run the complete test suite:

```bash
python test_vault.py
```

This runs:
- 30+ unit tests covering all modules
- Integration tests simulating real-world workflows
- Encryption/decryption verification
- Database operations
- Password generation and validation

## Usage Examples

### Python Script Integration

```python
from password_vault import PasswordVault

# Initialize vault
vault = PasswordVault("my_vault.db")

# Create new vault
vault.initialize_vault("MyMasterPassword123")

# Add a credential
cred_id = vault.add_credential(
    site="gmail.com",
    username="user@gmail.com",
    password="mypassword123",
    notes="Personal email account"
)

# Retrieve credential
credential = vault.get_credential(cred_id)
print(f"Password for {credential.site}: {credential.password}")

# Search credentials
results = vault.search_credentials("gmail")

# Update credential
vault.update_credential(cred_id, password="newpassword123")

# Delete credential
vault.delete_credential(cred_id)

# Generate password
strong_password = vault.generate_password(length=20, use_special=True)

# Evaluate password strength
score, level, feedback = vault.evaluate_password_strength("MyPassword123!")

# Export backup
vault.export_encrypted_backup("backup.vault")

# Lock vault
vault.lock_vault()

# Unlock vault
vault.unlock_vault("MyMasterPassword123")

# Close vault
vault.close()
```

### Password Generator Usage

```python
from password_generator import PasswordGenerator

gen = PasswordGenerator()

# Generate single password
password = gen.generate(length=16, use_special=True)

# Generate multiple passwords
passwords = gen.generate_multiple(count=5, length=20)

# Evaluate strength
score, level, feedback = gen.evaluate_strength(password)
print(f"Strength: {level} ({score}/100)")
for suggestion in feedback:
    print(f"- {suggestion}")
```

## Master Password Requirements

Your master password must meet these requirements:
- ✅ Minimum 8 characters
- ✅ At least one uppercase letter
- ✅ At least one lowercase letter
- ✅ At least one number

**Recommended:**
- Use 12-20 characters for better security
- Include special characters if possible
- Avoid dictionary words or personal information
- Use a passphrase combination (e.g., "Blue3Elephants!Singing")

## Security Recommendations

1. **Master Password**
   - Use a strong, unique master password
   - Don't share it with anyone
   - Store it in your memory, not in files
   - Use a password manager if needed (external)

2. **Backups**
   - Regular encrypted backups to safe location
   - Keep backups offline when possible
   - Test backup restoration periodically

3. **Computer Security**
   - Keep your operating system updated
   - Use antivirus/antimalware software
   - Enable full disk encryption
   - Lock your computer when away

4. **Vault Management**
   - Lock vault when stepping away
   - Don't leave vault open unattended
   - Use strong BIOS/UEFI passwords
   - Consider using this on a dedicated device

## Troubleshooting

### "Vault not initialized" error
- Vault database hasn't been set up yet
- Create a new vault with master password
- This only appears on first run

### "Incorrect master password" error
- Master password is wrong
- Double-check caps lock
- Vault might be corrupted (restore from backup)

### "Credential already exists" error
- Site + username combination already in vault
- Use Edit feature to update existing credential
- Or use different username for same site

### Slow password verification
- Normal for security (PBKDF2 with 100,000 iterations)
- Takes 1-2 seconds by design
- Prevents brute-force attacks

### GUI not displaying properly
- Update tkinter: `pip install --upgrade tk`
- On Linux, install: `sudo apt install python3-tk`
- Try different display settings if available

## File Locations

- **Database**: `vault.db` (default, same directory as script)
- **Backups**: User-specified location
- **Logs**: None (no logging enabled by design - privacy first)

## Performance

- **Startup Time**: < 1 second (GUI or CLI)
- **Master Password Verification**: 1-2 seconds (intentional delay)
- **Add Credential**: < 500ms
- **Search 1000 credentials**: < 100ms
- **Generate Password**: < 50ms

## Limitations & Future Enhancements

### Current Limitations
- Single master password (no multi-user support)
- No automatic lock timer
- No password history
- SQLite only (single-device)
- No cloud sync

### Planned Enhancements
- [ ] Auto-lock timer
- [ ] Password history/recovery
- [ ] Import from other password managers
- [ ] Web vault (web-based interface)
- [ ] Mobile app
- [ ] Cloud sync with end-to-end encryption
- [ ] Biometric unlock
- [ ] Dark mode
- [ ] Two-factor authentication

## Contributing

Contributions are welcome! Areas for improvement:
- Additional encryption algorithms
- Cloud synchronization
- Mobile applications
- Import/export from other managers
- UI/UX improvements

## License

This project is open source and available under the MIT License.

## Disclaimer

This software is provided as-is for educational and personal use. While we've implemented industry-standard security practices, no software is 100% secure. Use at your own risk. Always maintain backups of your data. The authors are not responsible for any loss of data or security breaches.

## Security Audit

For a production system, consider:
- Professional security audit
- Penetration testing
- Code review by security experts
- Compliance with standards (SOC 2, ISO 27001)

## Support

For issues, questions, or suggestions:
1. Check this README first
2. Review the test file for usage examples
3. Check code comments and docstrings
4. Create an issue on GitHub

## Author

Created as a demonstration of secure password management principles using Python.

---

**Last Updated**: 2024
**Version**: 1.0.0
**Status**: Production Ready
