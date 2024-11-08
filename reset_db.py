# backend/reset_db.py
import argparse
from sqlalchemy import inspect
from app.database import Base, engine, SessionLocal
from app import models  # This imports all models

def get_table_names():
    """Get all table names in the database"""
    inspector = inspect(engine)
    return inspector.get_table_names()

def drop_all_tables():
    """Drop all tables in the database"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully!")

def create_all_tables():
    """Create all tables in the database"""
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

def list_tables():
    """List all tables in the database"""
    tables = get_table_names()
    print("\nCurrent tables in database:")
    for table in tables:
        print(f"- {table}")

def reset_database(confirm=False):
    """Reset the database by dropping all tables and recreating them"""
    if not confirm:
        tables = get_table_names()
        if tables:
            print("\nWARNING: This will delete all data in the following tables:")
            for table in tables:
                print(f"- {table}")
            response = input("\nAre you sure you want to continue? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return
    
    drop_all_tables()
    create_all_tables()
    print("\nDatabase reset complete!")
    list_tables()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Database management utility')
    parser.add_argument('--list', action='store_true', help='List all tables')
    parser.add_argument('--create', action='store_true', help='Create all tables')
    parser.add_argument('--drop', action='store_true', help='Drop all tables')
    parser.add_argument('--reset', action='store_true', help='Reset database (drop and recreate all tables)')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompts')
    
    args = parser.parse_args()

    try:
        if args.list:
            list_tables()
        elif args.create:
            create_all_tables()
            list_tables()
        elif args.drop:
            if args.force or input("Are you sure you want to drop all tables? (y/N): ").lower() == 'y':
                drop_all_tables()
        elif args.reset:
            reset_database(confirm=args.force)
        else:
            # Default behavior
            print("\nAvailable commands:")
            print("  python reset_db.py --list   : List all tables")
            print("  python reset_db.py --create : Create all tables")
            print("  python reset_db.py --drop   : Drop all tables")
            print("  python reset_db.py --reset  : Reset database (drop and recreate)")
            print("  Add --force to skip confirmation prompts")
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise