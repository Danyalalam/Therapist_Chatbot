import sqlite3
from pathlib import Path
from passlib.context import CryptContext

# Define directories
ROOT_DIR = Path(__file__).resolve().parent
DATABASE_DIR = ROOT_DIR / 'database'
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATABASE_DIR / 'chatbot.db'

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Connect to SQLite database
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Create conversations table
c.execute('''
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    model TEXT NOT NULL,
    username TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username)
)
''')

conn.commit()
conn.close()

print(f"Database setup completed at {DATABASE_PATH}")