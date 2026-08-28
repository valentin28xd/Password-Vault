"""
GUI module for the password vault using tkinter.
Provides a user-friendly interface for vault operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from password_vault import PasswordVault
import threading


class PasswordVaultGUI:
    """
    Tkinter-based GUI for the password vault application.
    """

    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("Password Vault")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Initialize vault
        self.vault = PasswordVault()
        
        # Configure style
        self.setup_styles()
        
        # Create main interface
        self.create_login_screen()

    def setup_styles(self):
        """Configure tkinter styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors
        self.bg_color = "#f0f0f0"
        self.fg_color = "#333333"
        self.accent_color = "#0066cc"
        
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        style.configure('TButton', background=self.bg_color)
        style.configure('TFrame', background=self.bg_color)

    def create_login_screen(self):
        """Create the login/initialization screen."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(main_frame, text="Password Vault", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Check if vault is initialized
        try:
            hash_result = self.vault.db.get_master_password_hash()
            
            if hash_result is None:
                # New vault - show setup screen
                self.create_setup_screen(main_frame)
            else:
                # Existing vault - show login screen
                self.create_login_form(main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def create_setup_screen(self, parent):
        """Create the initial setup screen."""
        frame = ttk.LabelFrame(parent, text="Setup New Vault", padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = ttk.Label(
            frame,
            text="Create a master password to protect your vault.\n"
                 "This password must be at least 8 characters with uppercase, lowercase, and numbers.",
            font=("Arial", 10)
        )
        instructions.pack(pady=10)
        
        # Password input
        ttk.Label(frame, text="Master Password:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 0))
        password_entry = ttk.Entry(frame, show="*", width=40)
        password_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # Confirm password
        ttk.Label(frame, text="Confirm Password:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 0))
        confirm_entry = ttk.Entry(frame, show="*", width=40)
        confirm_entry.pack(anchor=tk.W, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def setup_vault():
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if not password or not confirm:
                messagebox.showwarning("Input Error", "Please enter a password")
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            try:
                self.vault.initialize_vault(password)
                messagebox.showinfo("Success", "Vault created successfully!")
                self.create_main_screen()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(button_frame, text="Create Vault", command=setup_vault).pack(side=tk.LEFT, padx=5)

    def create_login_form(self, parent):
        """Create the login form for existing vaults."""
        frame = ttk.LabelFrame(parent, text="Unlock Vault", padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Master Password:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 0))
        password_entry = ttk.Entry(frame, show="*", width=40)
        password_entry.pack(anchor=tk.W, pady=(0, 20))
        
        def login():
            password = password_entry.get()
            
            if not password:
                messagebox.showwarning("Input Error", "Please enter your master password")
                return
            
            try:
                self.vault.unlock_vault(password)
                messagebox.showinfo("Success", "Vault unlocked!")
                self.create_main_screen()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Unlock", command=login).pack(side=tk.LEFT, padx=5)

    def create_main_screen(self):
        """Create the main vault screen."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Backup", command=self.export_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Lock Vault", command=self.lock_and_exit)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Create main layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top bar with search and buttons
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_frame, text="Search:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        search_entry = ttk.Entry(top_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        def search():
            query = search_entry.get()
            if query:
                self.display_credentials(self.vault.search_credentials(query))
            else:
                self.display_all_credentials()
        
        ttk.Button(top_frame, text="Search", command=search).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Add New", command=self.show_add_credential_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Refresh", command=self.display_all_credentials).pack(side=tk.LEFT, padx=5)
        
        # Credentials table
        self.tree_frame = ttk.Frame(main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview columns
        columns = ("Site", "Username", "Actions")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, height=15)
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Site", anchor=tk.W, width=300)
        self.tree.column("Username", anchor=tk.W, width=300)
        self.tree.column("Actions", anchor=tk.CENTER, width=200)
        
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("Site", text="Site", anchor=tk.W)
        self.tree.heading("Username", text="Username", anchor=tk.W)
        self.tree.heading("Actions", text="Actions", anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click for viewing
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Display all credentials
        self.display_all_credentials()

    def display_all_credentials(self):
        """Display all credentials in the table."""
        try:
            credentials = self.vault.get_all_credentials()
            self.display_credentials(credentials)
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))

    def display_credentials(self, credentials):
        """Display credentials in the table."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add credentials
        for cred in credentials:
            actions = f"View | Edit | Delete"
            self.tree.insert("", tk.END, iid=cred.id,
                           values=(cred.site, cred.username, actions))

    def on_tree_double_click(self, event):
        """Handle double-click on credential."""
        selection = self.tree.selection()
        if selection:
            credential_id = selection[0]
            self.show_credential_details(credential_id)

    def show_credential_details(self, credential_id):
        """Show details of a credential in a new window."""
        try:
            cred = self.vault.get_credential(credential_id)
            
            if not cred:
                messagebox.showerror("Error", "Credential not found")
                return
            
            # Create detail window
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Credential Details - {cred.site}")
            detail_window.geometry("500x300")
            
            frame = ttk.Frame(detail_window, padding=20)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Display details
            ttk.Label(frame, text=f"Site: {cred.site}", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
            ttk.Label(frame, text=f"Username: {cred.username}", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
            
            # Password with copy button
            password_frame = ttk.Frame(frame)
            password_frame.pack(anchor=tk.W, fill=tk.X, pady=5)
            
            ttk.Label(password_frame, text="Password:", font=("Arial", 10)).pack(side=tk.LEFT)
            
            password_var = tk.StringVar(value=cred.password)
            ttk.Entry(password_frame, textvariable=password_var, width=30).pack(side=tk.LEFT, padx=5)
            
            def copy_password():
                self.root.clipboard_clear()
                self.root.clipboard_append(cred.password)
                messagebox.showinfo("Success", "Password copied to clipboard!")
            
            ttk.Button(password_frame, text="Copy", command=copy_password).pack(side=tk.LEFT)
            
            if cred.notes:
                ttk.Label(frame, text=f"Notes: {cred.notes}", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
            
            # Action buttons
            button_frame = ttk.Frame(frame)
            button_frame.pack(fill=tk.X, pady=20)
            
            ttk.Button(button_frame, text="Edit", 
                      command=lambda: self.show_edit_dialog(credential_id)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Delete",
                      command=lambda: self.delete_credential(credential_id, detail_window)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Close", command=detail_window.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_add_credential_dialog(self):
        """Show dialog to add a new credential."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Credential")
        dialog.geometry("400x350")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Site
        ttk.Label(frame, text="Site:").pack(anchor=tk.W)
        site_entry = ttk.Entry(frame, width=40)
        site_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # Username
        ttk.Label(frame, text="Username:").pack(anchor=tk.W)
        username_entry = ttk.Entry(frame, width=40)
        username_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # Password
        ttk.Label(frame, text="Password:").pack(anchor=tk.W)
        password_frame = ttk.Frame(frame)
        password_frame.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))
        
        password_entry = ttk.Entry(password_frame, width=30, show="*")
        password_entry.pack(side=tk.LEFT)
        
        def generate_password():
            generated = self.vault.generate_password()
            password_entry.delete(0, tk.END)
            password_entry.insert(0, generated)
        
        ttk.Button(password_frame, text="Generate", command=generate_password).pack(side=tk.LEFT, padx=5)
        
        # Show/Hide password
        show_var = tk.BooleanVar()
        
        def toggle_password():
            if show_var.get():
                password_entry.config(show="")
            else:
                password_entry.config(show="*")
        
        ttk.Checkbutton(frame, text="Show Password", variable=show_var,
                       command=toggle_password).pack(anchor=tk.W, pady=(0, 10))
        
        # Notes
        ttk.Label(frame, text="Notes:").pack(anchor=tk.W)
        notes_entry = ttk.Entry(frame, width=40)
        notes_entry.pack(anchor=tk.W, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        def add_credential():
            site = site_entry.get()
            username = username_entry.get()
            password = password_entry.get()
            notes = notes_entry.get()
            
            if not site or not username or not password:
                messagebox.showwarning("Input Error", "Please fill in all required fields")
                return
            
            try:
                self.vault.add_credential(site, username, password, notes)
                messagebox.showinfo("Success", "Credential added successfully!")
                dialog.destroy()
                self.display_all_credentials()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(button_frame, text="Add", command=add_credential).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def show_edit_dialog(self, credential_id):
        """Show dialog to edit a credential."""
        try:
            cred = self.vault.get_credential(credential_id)
            
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Edit Credential - {cred.site}")
            dialog.geometry("400x350")
            
            frame = ttk.Frame(dialog, padding=20)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Site
            ttk.Label(frame, text="Site:").pack(anchor=tk.W)
            site_entry = ttk.Entry(frame, width=40)
            site_entry.insert(0, cred.site)
            site_entry.pack(anchor=tk.W, pady=(0, 10))
            
            # Username
            ttk.Label(frame, text="Username:").pack(anchor=tk.W)
            username_entry = ttk.Entry(frame, width=40)
            username_entry.insert(0, cred.username)
            username_entry.pack(anchor=tk.W, pady=(0, 10))
            
            # Password
            ttk.Label(frame, text="Password:").pack(anchor=tk.W)
            password_entry = ttk.Entry(frame, width=40, show="*")
            password_entry.insert(0, cred.password)
            password_entry.pack(anchor=tk.W, pady=(0, 10))
            
            # Notes
            ttk.Label(frame, text="Notes:").pack(anchor=tk.W)
            notes_entry = ttk.Entry(frame, width=40)
            notes_entry.insert(0, cred.notes)
            notes_entry.pack(anchor=tk.W, pady=(0, 20))
            
            # Buttons
            button_frame = ttk.Frame(frame)
            button_frame.pack(fill=tk.X)
            
            def update_credential():
                try:
                    self.vault.update_credential(
                        credential_id,
                        site=site_entry.get(),
                        username=username_entry.get(),
                        password=password_entry.get(),
                        notes=notes_entry.get()
                    )
                    messagebox.showinfo("Success", "Credential updated!")
                    dialog.destroy()
                    self.display_all_credentials()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            ttk.Button(button_frame, text="Update", command=update_credential).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_credential(self, credential_id, parent_window=None):
        """Delete a credential with confirmation."""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this credential?"):
            try:
                self.vault.delete_credential(credential_id)
                messagebox.showinfo("Success", "Credential deleted!")
                if parent_window:
                    parent_window.destroy()
                self.display_all_credentials()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_backup(self):
        """Export credentials to encrypted backup file."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".vault",
                filetypes=[("Vault Backup", "*.vault"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            
            if file_path:
                self.vault.export_encrypted_backup(file_path)
                messagebox.showinfo("Success", f"Backup exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def lock_and_exit(self):
        """Lock the vault and return to login."""
        self.vault.lock_vault()
        self.create_login_screen()

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", 
            "Password Vault v1.0\n\n"
            "A secure password manager using Fernet encryption\n"
            "and SQLite database.\n\n"
            "Created with Python and Tkinter")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = PasswordVaultGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
