# Quick Start Guide

Get started with Password Vault in 5 minutes!

## Installation

### 1. Install Python (if not already installed)
- Download from [python.org](https://www.python.org)
- Ensure Python 3.8+ is installed
- Verify: `python --version`

### 2. Clone/Download the Project
```bash
# Option A: Clone from GitHub
git clone https://github.com/yourusername/password-vault.git
cd password-vault

# Option B: Download ZIP and extract
# (extract the downloaded ZIP file)
cd password-vault
```

### 3. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## First Run

### Option A: GUI (Recommended for Most Users)

```bash
python main.py
```

1. **First Launch:**
   - Click "1" or "GUI" to start the graphical interface
   - Choose your master password (8+ characters, uppercase, lowercase, numbers)
   - Confirm the password
   - Click "Create Vault"

2. **Daily Usage:**
   - Launch: `python main.py`
   - Enter master password
   - Click "Unlock"
   - Use the interface to manage passwords

### Option B: CLI (For Power Users)

```bash
python main.py --interface cli
```

1. **First Launch:**
   - Create master password when prompted
   - Use numeric menu to navigate

2. **Menu Options:**
   - `1` - List all credentials
   - `2` - View a credential
   - `3` - Add new credential
   - `4` - Edit credential
   - `5` - Delete credential
   - `6` - Search credentials
   - `7` - Generate password
   - `8` - Export backup
   - `9` - Lock vault
   - `0` - Exit

## Common Tasks

### Adding Your First Credential

**GUI:**
1. Click "Add New"
2. Enter site name (e.g., "gmail.com")
3. Enter username/email
4. Either type password or click "Generate"
5. Add optional notes
6. Click "Add"

**CLI:**
1. Select option `3` from menu
2. Enter site, username, password (or generate)
3. Add optional notes

### Finding a Credential

**GUI:**
1. Use search box at top
2. Type site name or username
3. Click "Search"

**CLI:**
1. Select option `6` from menu
2. Type search term

### Viewing Password

**GUI:**
1. Double-click credential in list
2. Password displayed in detail window
3. Click "Copy" to copy to clipboard

**CLI:**
1. List all credentials (option `1`)
2. Select option `2` to view
3. Enter credential ID
4. Password displayed

### Changing a Password

**GUI:**
1. View credential details
2. Click "Edit"
3. Enter new password
4. Click "Update"

**CLI:**
1. List credentials (option `1`)
2. Select option `4` to edit
3. Enter new password when prompted
4. Leave blank to keep current value

### Generating a Strong Password

**GUI:**
1. Add New credential (or Edit existing)
2. Click "Generate" button
3. Generated password appears in field

**CLI:**
1. Select option `7` from menu
2. Choose desired settings (length, character types)
3. Password generated and displayed
4. Strength evaluated automatically

### Creating a Backup

**GUI:**
1. Click "File" → "Export Backup"
2. Choose location and filename
3. Backup created as encrypted .vault file

**CLI:**
1. Select option `8` from menu
2. Enter backup filename (or press Enter for default)
3. Backup saved to specified location

## Master Password Tips

✅ **Good Master Passwords:**
- MyDog3Barks!Loudly
- Coffee2023@Morning
- SecurePass456#Blue
- Elephant5Dances$Fast

❌ **Bad Master Passwords:**
- password123
- qwerty
- 12345678
- MyName2024

## Keyboard Shortcuts

### GUI
- `Ctrl+Q` - Exit application
- `Tab` - Navigate between fields
- `Enter` - Submit form

### CLI
- `Ctrl+C` - Exit application
- Arrow keys - Navigate menu

## Troubleshooting

### "ModuleNotFoundError: No module named 'cryptography'"
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### "Incorrect master password"
- Check that Caps Lock is off
- Re-enter password carefully
- If you forgot it, database cannot be recovered

### GUI not opening
```bash
# Install tkinter (Linux)
sudo apt install python3-tk

# Update tkinter (All platforms)
pip install --upgrade tk
```

### Database locked error
- Exit the application
- Delete `vault.db` (backup first if important)
- Restart the application

## Next Steps

1. **Add Credentials:** Add all your important passwords
2. **Test Retrieval:** Make sure you can retrieve passwords easily
3. **Create Backup:** Export encrypted backup to safe location
4. **Secure Storage:** Keep backup in safe place (external drive, cloud storage)
5. **Test Recovery:** Verify backup works by restoring later

## Security Reminders

🔐 **Remember:**
- Your master password cannot be recovered
- Store master password in your memory
- Regular backups to safe location
- Lock vault when stepping away
- Keep software updated

## Advanced Usage

### Import Passwords from Text File

```python
# Create a script like this
from password_vault import PasswordVault

vault = PasswordVault()
vault.unlock_vault("your_master_password")

# Add passwords from list
credentials = [
    ("gmail.com", "user@gmail.com", "password123"),
    ("github.com", "username", "gitpassword"),
]

for site, user, pass_word in credentials:
    vault.add_credential(site, user, pass_word)
```

### Run Tests

```bash
python test_vault.py
```

### Run with Custom Database

```bash
python main.py --db /path/to/custom/vault.db
```

## Getting Help

### Documentation
- `README.md` - Full documentation
- `DEVELOPMENT.md` - Developer guide
- Code comments - Inline documentation

### Troubleshooting
1. Check README.md troubleshooting section
2. Review docstrings in code files
3. Check error messages carefully

## What's Next?

- ✅ Basic password management
- 📚 Read full README.md for advanced features
- 🔧 Explore CLI interface if you prefer command line
- 🧪 Run tests to verify installation
- 💾 Set up regular backup schedule

---

**Quick Reference:**

| Task | GUI | CLI |
|------|-----|-----|
| Launch | `python main.py` | `python main.py --cli` |
| Add password | Add New button | Menu option 3 |
| View password | Double-click entry | Menu option 2 |
| Search | Search box | Menu option 6 |
| Generate password | Generate button | Menu option 7 |
| Backup | File → Export | Menu option 8 |

---

**Having issues?** Check the [Full Documentation](README.md)
