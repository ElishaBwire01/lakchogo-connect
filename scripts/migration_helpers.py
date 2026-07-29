#!/usr/bin/env python
"""
Migration helpers for LakChogo Connect.
Run this script to fix common migration issues.
"""

import os
import sys
import django
import subprocess

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def reset_migrations():
    """Reset all migrations"""
    print("=" * 60)
    print("LAKCHOGO CONNECT - MIGRATION RESET")
    print("=" * 60)
    
    confirm = input("\n⚠️ This will DELETE all migrations and the database! Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Reset cancelled.")
        return
    
    # Delete database
    print("\n🗑️ Deleting database...")
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
    if os.path.exists(db_path):
        os.remove(db_path)
        print("  ✅ Database deleted.")
    else:
        print("  ℹ️ No database found.")
    
    # Delete migrations
    print("\n🗑️ Deleting migrations...")
    apps = ['accounts', 'members', 'finance', 'meetings', 'compliance', 'welfare', 'communications', 'dashboard', 'reports', 'api']
    for app in apps:
        migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), app, 'migrations')
        if os.path.exists(migrations_dir):
            # Keep __init__.py
            for file in os.listdir(migrations_dir):
                if file != '__init__.py' and file.endswith('.py'):
                    os.remove(os.path.join(migrations_dir, file))
                elif file.endswith('.pyc'):
                    os.remove(os.path.join(migrations_dir, file))
            print(f"  ✅ Cleaned {app}/migrations/")
    
    print("\n📦 Creating fresh migrations...")
    for app in apps:
        try:
            call_command('makemigrations', app, verbosity=0)
            print(f"  ✅ Created migrations for {app}")
        except Exception as e:
            print(f"  ❌ Error creating migrations for {app}: {e}")
    
    print("\n📦 Applying migrations...")
    try:
        call_command('migrate', verbosity=0)
        print("  ✅ Migrations applied successfully!")
    except Exception as e:
        print(f"  ❌ Error applying migrations: {e}")
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION RESET COMPLETE!")
    print("=" * 60)

def check_migrations():
    """Check migration status"""
    print("=" * 60)
    print("LAKCHOGO CONNECT - MIGRATION CHECK")
    print("=" * 60)
    
    from django.db.migrations.loader import MigrationLoader
    loader = MigrationLoader(connection)
    
    print("\n📊 Migration Status:")
    for app in loader.migrations:
        app_migrations = loader.migrations[app]
        applied = loader.applied_migrations
        for migration in app_migrations:
            status = "✅" if (app, migration.name) in applied else "❌"
            print(f"  {status} {app}.{migration.name}")
    
    print("\n" + "=" * 60)

def fix_migration_dependencies():
    """Fix migration dependencies"""
    print("=" * 60)
    print("LAKCHOGO CONNECT - FIX DEPENDENCIES")
    print("=" * 60)
    
    print("\n🔧 Fixing migration dependencies...")
    
    # Run migrations with fake-initial for consistency
    try:
        call_command('migrate', '--fake-initial', verbosity=0)
        print("  ✅ Migration dependencies fixed!")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)

def show_help():
    """Show help"""
    print("=" * 60)
    print("LAKCHOGO CONNECT - MIGRATION HELPERS")
    print("=" * 60)
    print("""
Commands:
  1. python scripts/migration_helpers.py reset     - Reset all migrations
  2. python scripts/migration_helpers.py check     - Check migration status
  3. python scripts/migration_helpers.py fix       - Fix migration dependencies
  4. python scripts/migration_helpers.py help      - Show this help
    """)

if __name__ == '__main__':
    args = sys.argv[1:] if len(sys.argv) > 1 else ['help']
    command = args[0] if args else 'help'
    
    if command == 'reset':
        reset_migrations()
    elif command == 'check':
        check_migrations()
    elif command == 'fix':
        fix_migration_dependencies()
    else:
        show_help()
