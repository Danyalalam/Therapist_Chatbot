# Therapist_Chatbot/setup_db.py
import os
import sqlite3
from pathlib import Path

def setup_database():
    try:
        # Define the database path
        ROOT_DIR = Path(__file__).resolve().parent
        DATABASE_DIR = ROOT_DIR / 'database'
        DATABASE_PATH = DATABASE_DIR / 'chatbot.db'
        
        # Create the database directory if it doesn't exist
        os.makedirs(DATABASE_DIR, exist_ok=True)
        
        # Delete existing database file if it exists
        if DATABASE_PATH.exists():
            print(f"Removing existing database at {DATABASE_PATH}")
            os.remove(DATABASE_PATH)
        
        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Create the conversations table with the 'model' column
        c.execute('''
            CREATE TABLE conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                model TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"Database created successfully at {DATABASE_PATH}")
    except Exception as e:
        print(f"Error creating database: {e}")
        raise

if __name__ == "__main__":
    setup_database()