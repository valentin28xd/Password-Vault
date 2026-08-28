"""
Command-line interface for the password vault.
Provides a terminal-based interface for vault operations.
"""

import sys
import getpass
from password_vault import PasswordVault
from tabulate import tabulate


class PasswordVaultCLI:
    """
    Command-line interface for the password vault.
    """

    def __init__(self, db_path: str = "vault.db"):
        """
        Initialize the CLI.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.vault = PasswordVault(db_path)
        self.running = True

    def run(self):
        """Run the CLI application."""
        print("\n" + "="*50)
        print("   PASSWORD VAULT - COMMAND LINE INTERFACE")
        print("="*50)
        
        try:
            self._initialize_or_login()
            self._main_menu()
        except KeyboardInterrupt:
            print("\n\nVault locked. Goodbye!")
            self.vault.close()
        except Exception as e:
            print(f"\nFatal error: {str(e)}")
            self.vault.close()

    def _initialize_or_login(self):
        """Initialize new vault or login to existing one."""
        try:
            hash_result = self.vault.db.get_master_password_hash()
            
            if hash_result is None:
                self._setup_new_vault()
            else:
                self._login_to_vault()
        except RuntimeError as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

    def _setup_new_vault(self):
        """Setup a new vault."""
        print("\n[NEW VAULT SETUP]")
        print("Create a master password to protect your vault.")
        print("Requirements: 8+ characters, uppercase, lowercase, and numbers\n")
        
        while True:
            password = getpass.getpass("Master Password: ")
            confirm = getpass.getpass("Confirm Password: ")
            
            if password != confirm:
                print("Passwords do not match. Try again.")
                continue
            
            try:
                self.vault.initialize_vault(password)
                print("\n✓ Vault created successfully!")
                break
            except ValueError as e:
                print(f"Error: {str(e)}")

    def _login_to_vault(self):
        """Login to existing vault."""
        print("\n[VAULT LOGIN]")
        
        while not self.vault.is_authenticated:
            password = getpass.getpass("Master Password: ")
            
            try:
                self.vault.unlock_vault(password)
                print("\n✓ Vault unlocked!")
            except ValueError as e:
                print(f"Error: {str(e)}")
                print("Try again.\n")

    def _main_menu(self):
        """Display main menu."""
        while self.running:
            print("\n" + "-"*50)
            print("[MAIN MENU]")
            print("-"*50)
            print("1. List all credentials")
            print("2. View credential")
            print("3. Add new credential")
            print("4. Edit credential")
            print("5. Delete credential")
            print("6. Search credentials")
            print("7. Generate password")
            print("8. Export backup")
            print("9. Lock vault")
            print("0. Exit")
            print("-"*50)
            
            choice = input("Enter choice (0-9): ").strip()
            
            if choice == "1":
                self._list_credentials()
            elif choice == "2":
                self._view_credential()
            elif choice == "3":
                self._add_credential()
            elif choice == "4":
                self._edit_credential()
            elif choice == "5":
                self._delete_credential()
            elif choice == "6":
                self._search_credentials()
            elif choice == "7":
                self._generate_password()
            elif choice == "8":
                self._export_backup()
            elif choice == "9":
                self.vault.lock_vault()
                self._login_to_vault()
            elif choice == "0":
                self.running = False
            else:
                print("Invalid choice. Try again.")

    def _list_credentials(self):
        """List all credentials."""
        try:
            credentials = self.vault.get_all_credentials()
            
            if not credentials:
                print("\nNo credentials found.")
                return
            
            print("\n[ALL CREDENTIALS]")
            print("-"*70)
            
            table_data = []
            for cred in credentials:
                table_data.append([cred.id, cred.site, cred.username, "●●●●●●●●"])
            
            headers = ["ID", "Site", "Username", "Password"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"Error: {str(e)}")

    def _view_credential(self):
        """View a specific credential."""
        try:
            self._list_credentials()
            
            credential_id = input("\nEnter credential ID to view: ").strip()
            
            if not credential_id.isdigit():
                print("Invalid ID.")
                return
            
            cred = self.vault.get_credential(int(credential_id))
            
            if not cred:
                print("Credential not found.")
                return
            
            print("\n[CREDENTIAL DETAILS]")
            print("-"*50)
            print(f"Site:     {cred.site}")
            print(f"Username: {cred.username}")
            print(f"Password: {cred.password}")
            if cred.notes:
                print(f"Notes:    {cred.notes}")
            print("-"*50)
        except Exception as e:
            print(f"Error: {str(e)}")

    def _add_credential(self):
        """Add a new credential."""
        try:
            print("\n[ADD NEW CREDENTIAL]")
            
            site = input("Site/Service name: ").strip()
            username = input("Username/Email: ").strip()
            
            use_generated = input("Generate password? (y/n): ").strip().lower()
            
            if use_generated == 'y':
                password = self.vault.generate_password()
                print(f"Generated password: {password}")
            else:
                password = getpass.getpass("Password: ")
            
            notes = input("Notes (optional): ").strip()
            
            self.vault.add_credential(site, username, password, notes)
            print("\n✓ Credential added successfully!")
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def _edit_credential(self):
        """Edit an existing credential."""
        try:
            self._list_credentials()
            
            credential_id = input("\nEnter credential ID to edit: ").strip()
            
            if not credential_id.isdigit():
                print("Invalid ID.")
                return
            
            cred = self.vault.get_credential(int(credential_id))
            
            if not cred:
                print("Credential not found.")
                return
            
            print("\n[EDIT CREDENTIAL]")
            print("Leave blank to keep current value\n")
            
            new_site = input(f"Site [{cred.site}]: ").strip()
            new_username = input(f"Username [{cred.username}]: ").strip()
            new_password = getpass.getpass("New password (leave blank to keep): ")
            new_notes = input(f"Notes [{cred.notes}]: ").strip()
            
            self.vault.update_credential(
                int(credential_id),
                site=new_site if new_site else None,
                username=new_username if new_username else None,
                password=new_password if new_password else None,
                notes=new_notes if new_notes else None
            )
            print("\n✓ Credential updated successfully!")
        except Exception as e:
            print(f"Error: {str(e)}")

    def _delete_credential(self):
        """Delete a credential."""
        try:
            self._list_credentials()
            
            credential_id = input("\nEnter credential ID to delete: ").strip()
            
            if not credential_id.isdigit():
                print("Invalid ID.")
                return
            
            confirm = input("Are you sure? (y/n): ").strip().lower()
            
            if confirm == 'y':
                self.vault.delete_credential(int(credential_id))
                print("\n✓ Credential deleted successfully!")
            else:
                print("Deletion cancelled.")
        except Exception as e:
            print(f"Error: {str(e)}")

    def _search_credentials(self):
        """Search for credentials."""
        try:
            query = input("\nSearch query (site or username): ").strip()
            
            if not query:
                print("No search query entered.")
                return
            
            results = self.vault.search_credentials(query)
            
            if not results:
                print("No credentials found.")
                return
            
            print("\n[SEARCH RESULTS]")
            print("-"*70)
            
            table_data = []
            for cred in results:
                table_data.append([cred.id, cred.site, cred.username, "●●●●●●●●"])
            
            headers = ["ID", "Site", "Username", "Password"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"Error: {str(e)}")

    def _generate_password(self):
        """Generate a password."""
        print("\n[PASSWORD GENERATOR]")
        
        try:
            length_input = input("Password length (default 16): ").strip()
            length = int(length_input) if length_input else 16
            
            include_uppercase = input("Include uppercase? (y/n, default y): ").strip().lower() != 'n'
            include_digits = input("Include digits? (y/n, default y): ").strip().lower() != 'n'
            include_special = input("Include special characters? (y/n, default y): ").strip().lower() != 'n'
            
            password = self.vault.generate_password(
                length=length,
                use_uppercase=include_uppercase,
                use_digits=include_digits,
                use_special=include_special
            )
            
            score, level, feedback = self.vault.evaluate_password_strength(password)
            
            print("\n[GENERATED PASSWORD]")
            print("-"*50)
            print(f"Password:  {password}")
            print(f"Strength:  {level} ({score}/100)")
            if feedback:
                print("Suggestions:")
                for suggestion in feedback:
                    print(f"  - {suggestion}")
            print("-"*50)
        except ValueError as e:
            print(f"Error: {str(e)}")

    def _export_backup(self):
        """Export credentials to backup file."""
        try:
            file_path = input("\nEnter backup file path (default: vault_backup.vault): ").strip()
            
            if not file_path:
                file_path = "vault_backup.vault"
            
            self.vault.export_encrypted_backup(file_path)
            print(f"\n✓ Backup exported to: {file_path}")
        except Exception as e:
            print(f"Error: {str(e)}")


def main():
    """Main entry point for the CLI application."""
    cli = PasswordVaultCLI()
    cli.run()


if __name__ == "__main__":
    main()
