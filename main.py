"""
Main entry point for the Password Vault application.
Allows user to choose between GUI and CLI interfaces.
"""

import sys
import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Password Vault - Secure Password Manager"
    )
    
    parser.add_argument(
        '--interface',
        choices=['gui', 'cli'],
        default=None,
        help='Choose interface: gui (default) or cli'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test suite'
    )
    
    parser.add_argument(
        '--db',
        default='vault.db',
        help='Path to vault database (default: vault.db)'
    )
    
    args = parser.parse_args()
    
    # Run tests if requested
    if args.test:
        print("Running test suite...\n")
        try:
            from test_vault import run_tests
            success = run_tests()
            sys.exit(0 if success else 1)
        except ImportError as e:
            print(f"Error: Could not import test module: {e}")
            sys.exit(1)
    
    # Determine which interface to use
    interface = args.interface
    
    if not interface:
        print("Password Vault - Secure Password Manager")
        print("=" * 50)
        print("\nChoose interface:")
        print("1. GUI (Graphical User Interface) - Recommended")
        print("2. CLI (Command Line Interface)")
        print()
        
        choice = input("Enter choice (1 or 2, default 1): ").strip() or "1"
        
        if choice == "1":
            interface = "gui"
        elif choice == "2":
            interface = "cli"
        else:
            print("Invalid choice. Defaulting to GUI.")
            interface = "gui"
    
    # Launch selected interface
    try:
        if interface == "gui":
            print("Launching GUI...")
            from gui import main as gui_main
            gui_main()
        else:  # cli
            from cli import PasswordVaultCLI
            cli = PasswordVaultCLI(args.db)
            cli.run()
    except ImportError as e:
        print(f"Error: Could not import {interface} module: {e}")
        print("\nMake sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nExiting Password Vault.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
