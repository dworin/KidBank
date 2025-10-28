"""Account management and business logic."""

import random
from typing import Optional, List
from .database import Database
from .currency import is_valid_currency


class AccountManager:
    """Manages account operations."""

    def __init__(self, database: Database):
        """Initialize account manager.

        Args:
            database: Database instance for persistence
        """
        self.db = database

    def generate_account_number(self, account_type: str) -> str:
        """Generate a unique 6-digit account number.

        Args:
            account_type: Type of account (checking or savings)

        Returns:
            Unique 6-digit account number
        """
        while True:
            # Generate 6-digit account number
            number = f"{random.randint(100000, 999999)}"

            # Check if unique
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM accounts WHERE account_number = ?", (number,))
            if cursor.fetchone() is None:
                return number

    def create_account(self, first_name: str, last_name: str, account_type: str, currency: str, initial_deposit: float = 0.0) -> dict:
        """Create a new account.

        Args:
            first_name: Account holder's first name
            last_name: Account holder's last name
            account_type: Type of account (checking or savings)
            currency: Currency code (e.g., 'USD', 'BB')
            initial_deposit: Initial deposit amount

        Returns:
            Dictionary with account details
        """
        if not first_name or not first_name.strip():
            raise ValueError("First name is required")

        if not last_name or not last_name.strip():
            raise ValueError("Last name is required")

        if account_type not in ["checking", "savings"]:
            raise ValueError("Account type must be 'checking' or 'savings'")

        if not is_valid_currency(currency):
            raise ValueError(f"Invalid currency: {currency}")

        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")

        account_number = self.generate_account_number(account_type)

        conn = self.db.connect()
        cursor = conn.cursor()

        # Create account
        cursor.execute("""
            INSERT INTO accounts (account_number, first_name, last_name, account_type, currency, balance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (account_number, first_name.strip(), last_name.strip(), account_type, currency, initial_deposit))

        account_id = cursor.lastrowid

        # Record initial deposit transaction if > 0
        if initial_deposit > 0:
            cursor.execute("""
                INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description)
                VALUES (?, ?, ?, ?, ?)
            """, (account_id, "deposit", initial_deposit, initial_deposit, "Initial deposit"))

        conn.commit()

        return {
            "id": account_id,
            "account_number": account_number,
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "account_type": account_type,
            "currency": currency,
            "balance": initial_deposit
        }

    def get_account(self, account_number: str) -> Optional[dict]:
        """Get account details by account number.

        Args:
            account_number: The account number to look up

        Returns:
            Dictionary with account details or None if not found
        """
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, account_number, first_name, last_name, account_type, currency, balance, created_at
            FROM accounts WHERE account_number = ?
        """, (account_number,))

        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "account_number": row["account_number"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "account_type": row["account_type"],
                "currency": row["currency"],
                "balance": row["balance"],
                "created_at": row["created_at"]
            }
        return None

    def list_accounts(self) -> List[dict]:
        """Get all accounts.

        Returns:
            List of account dictionaries
        """
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, account_number, first_name, last_name, account_type, currency, balance, created_at
            FROM accounts ORDER BY last_name, first_name
        """)

        return [
            {
                "id": row["id"],
                "account_number": row["account_number"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "account_type": row["account_type"],
                "currency": row["currency"],
                "balance": row["balance"],
                "created_at": row["created_at"]
            }
            for row in cursor.fetchall()
        ]

    def get_transactions(self, account_number: str, limit: int = 10) -> List[dict]:
        """Get recent transactions for an account.

        Args:
            account_number: The account number
            limit: Maximum number of transactions to return (default 10)

        Returns:
            List of transaction dictionaries, most recent first
        """
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.transaction_type, t.amount, t.balance_after,
                   t.description, t.created_at
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.account_number = ?
            ORDER BY t.created_at DESC
            LIMIT ?
        """, (account_number, limit))

        return [
            {
                "id": row["id"],
                "transaction_type": row["transaction_type"],
                "amount": row["amount"],
                "balance_after": row["balance_after"],
                "description": row["description"],
                "created_at": row["created_at"]
            }
            for row in cursor.fetchall()
        ]

    def deposit(self, account_number: str, amount: float, description: str = "") -> dict:
        """Make a deposit to an account.

        Args:
            account_number: The account number
            amount: Amount to deposit (must be positive)
            description: Optional transaction description

        Returns:
            Dictionary with transaction details

        Raises:
            ValueError: If amount is not positive or account not found
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        account = self.get_account(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")

        new_balance = account["balance"] + amount

        conn = self.db.connect()
        cursor = conn.cursor()

        # Update account balance
        cursor.execute("""
            UPDATE accounts SET balance = ? WHERE account_number = ?
        """, (new_balance, account_number))

        # Record transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description)
            VALUES (?, ?, ?, ?, ?)
        """, (account["id"], "deposit", amount, new_balance, description or "Deposit"))

        conn.commit()

        return {
            "account_number": account_number,
            "transaction_type": "deposit",
            "amount": amount,
            "new_balance": new_balance
        }

    def withdraw(self, account_number: str, amount: float, description: str = "") -> dict:
        """Make a withdrawal from an account.

        Args:
            account_number: The account number
            amount: Amount to withdraw (must be positive)
            description: Optional transaction description

        Returns:
            Dictionary with transaction details

        Raises:
            ValueError: If amount is invalid, insufficient funds, or account not found
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        account = self.get_account(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")

        if account["balance"] < amount:
            raise ValueError("Insufficient funds")

        new_balance = account["balance"] - amount

        conn = self.db.connect()
        cursor = conn.cursor()

        # Update account balance
        cursor.execute("""
            UPDATE accounts SET balance = ? WHERE account_number = ?
        """, (new_balance, account_number))

        # Record transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description)
            VALUES (?, ?, ?, ?, ?)
        """, (account["id"], "withdrawal", amount, new_balance, description or "Withdrawal"))

        conn.commit()

        return {
            "account_number": account_number,
            "transaction_type": "withdrawal",
            "amount": amount,
            "new_balance": new_balance
        }
