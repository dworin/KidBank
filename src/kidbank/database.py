"""Database management for Kidbank."""

import sqlite3
from pathlib import Path
from typing import Optional


class Database:
    """Manages SQLite database connections and schema."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file. Defaults to ~/.kidbank/kidbank.db
        """
        if db_path is None:
            db_path = Path.home() / ".kidbank" / "kidbank.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Establish database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self._initialize_schema()
        return self.conn

    def _initialize_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                account_type TEXT NOT NULL,
                currency TEXT NOT NULL DEFAULT 'USD',
                balance REAL NOT NULL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add name columns to existing tables (for migration)
        try:
            cursor.execute("ALTER TABLE accounts ADD COLUMN first_name TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE accounts ADD COLUMN last_name TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE accounts ADD COLUMN currency TEXT DEFAULT 'USD'")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                balance_after REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)

        self.conn.commit()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
