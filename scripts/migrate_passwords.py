#!/usr/bin/env python3
"""
Password Migration Script for Boot-Monitoring Application

This script migrates user passwords from the old SHA-256 hashing method
to the more secure bcrypt hashing method.

IMPORTANT: Run this script ONCE after updating the application code to use bcrypt.

Usage:
    python scripts/migrate_passwords.py

The script will:
1. Backup the existing database
2. Prompt for the plaintext password of each user (or use default if known)
3. Re-hash passwords using bcrypt
4. Update the database with new password hashes

NOTE: This script requires users to provide their plaintext passwords,
or you'll need to know the default credentials. Alternatively, users can
reset their passwords after migration.
"""

import sqlite3
import bcrypt
import os
import shutil
from datetime import datetime
from getpass import getpass


def backup_database(db_path):
    """Create a backup of the database before migration."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"

    try:
        shutil.copy2(db_path, backup_path)
        print(f"✓ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"✗ Failed to backup database: {e}")
        raise


def hash_password_bcrypt(password):
    """Hash password using bcrypt (same as in User model)."""
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')


def migrate_passwords(db_path, default_password=None):
    """
    Migrate user passwords from SHA-256 to bcrypt.

    Args:
        db_path: Path to the SQLite database
        default_password: Optional default password to use for all users
    """
    if not os.path.exists(db_path):
        print(f"✗ Database not found: {db_path}")
        return False

    # Backup database first
    try:
        backup_path = backup_database(db_path)
    except Exception as e:
        print(f"Migration aborted due to backup failure.")
        return False

    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Get all users
        cursor.execute('SELECT id, username, password_hash FROM users')
        users = cursor.fetchall()

        if not users:
            print("No users found in database.")
            return True

        print(f"\nFound {len(users)} user(s) to migrate.\n")

        migrated_count = 0

        for user in users:
            user_id = user['id']
            username = user['username']
            old_hash = user['password_hash']

            # Check if password is already bcrypt (starts with $2b$ or $2a$)
            if old_hash.startswith('$2b$') or old_hash.startswith('$2a$'):
                print(f"⊳ User '{username}' already uses bcrypt - skipping")
                continue

            print(f"\n--- Migrating user: {username} ---")

            if default_password:
                password = default_password
                print(f"Using default password for '{username}'")
            else:
                print(f"Please enter the plaintext password for '{username}'")
                print("(or press Enter to skip this user)")
                password = getpass("Password: ")

                if not password:
                    print(f"⊳ Skipping user '{username}'")
                    continue

            # Hash with bcrypt
            new_hash = hash_password_bcrypt(password)

            # Update database
            cursor.execute(
                'UPDATE users SET password_hash = ? WHERE id = ?',
                (new_hash, user_id)
            )

            print(f"✓ Successfully migrated password for '{username}'")
            migrated_count += 1

        # Commit changes
        conn.commit()

        print(f"\n{'='*60}")
        print(f"Migration completed successfully!")
        print(f"Migrated: {migrated_count}/{len(users)} users")
        print(f"Backup saved to: {backup_path}")
        print(f"{'='*60}\n")

        return True

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        print(f"Database has been rolled back.")
        print(f"You can restore from backup: {backup_path}")
        return False

    finally:
        conn.close()


def main():
    """Main migration function."""
    print("="*60)
    print("Boot-Monitoring Password Migration Script")
    print("="*60)
    print("\nThis script will migrate passwords from SHA-256 to bcrypt.")
    print("A backup of the database will be created automatically.\n")

    # Determine database path
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    try:
        from config import get_config
        config = get_config()
        db_path = config.DATABASE_PATH
        default_password = config.DEFAULT_PASSWORD if hasattr(config, 'DEFAULT_PASSWORD') else None
    except Exception as e:
        print(f"Could not load configuration: {e}")
        db_path = input("Enter database path (default: dev_users.db): ") or 'dev_users.db'
        default_password = None

    print(f"Database: {db_path}\n")

    # Ask if user wants to use default password for all users
    use_default = False
    if default_password:
        response = input(f"Use default password (from config) for all users? [y/N]: ")
        use_default = response.lower() == 'y'
        if not use_default:
            default_password = None

    response = input("\nProceed with migration? [y/N]: ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return

    success = migrate_passwords(db_path, default_password)

    if success:
        print("\n✓ Migration completed successfully!")
        print("\nIMPORTANT: Please restart the application to use the new password hashing.")
        print("Users who were skipped will need to reset their passwords.")
    else:
        print("\n✗ Migration failed. Please check the error messages above.")
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
