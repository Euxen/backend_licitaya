# backend/reset_db.py
from app.database import Base, engine
from app import models  # This imports the User model

def reset_database():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database setup complete!")

if __name__ == "__main__":
    reset_database()