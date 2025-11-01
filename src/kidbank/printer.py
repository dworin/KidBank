"""Printer functionality for receipts and statements."""

import subprocess
from datetime import datetime
from typing import List, Dict, Optional
from .currency import get_currency


class PrinterError(Exception):
    """Exception raised when printing fails."""
    pass


class Printer:
    """Handles printing of receipts and statements using lp command."""

    WIDTH = 80  # Standard terminal width for retro aesthetic

    @staticmethod
    def _center(text: str, width: int = WIDTH) -> str:
        """Center text within given width."""
        return text.center(width)

    @staticmethod
    def _line(char: str = "=", width: int = WIDTH) -> str:
        """Generate a line of characters."""
        return char * width

    @staticmethod
    def _format_datetime(dt_str: str) -> str:
        """Format datetime string for display."""
        try:
            # Parse the datetime string from database
            dt = datetime.fromisoformat(dt_str.replace(" ", "T"))
            return dt.strftime("%m/%d/%Y %I:%M:%S %p")
        except:
            return dt_str

    @staticmethod
    def format_receipt(account: Dict, transaction: Dict, transaction_id: int) -> str:
        """Format a transaction receipt.

        Args:
            account: Account dictionary with holder info, number, balance, currency
            transaction: Transaction dictionary with type, amount, new_balance
            transaction_id: ID of the transaction

        Returns:
            Formatted receipt as string
        """
        currency = get_currency(account["currency"])
        now = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

        # Get transaction details
        txn_type = transaction["transaction_type"].upper()
        amount = transaction["amount"]
        new_balance = transaction["new_balance"]
        description = transaction.get("description", "")

        lines = [
            "",
            Printer._line("*"),
            Printer._center("KIDBANK TERMINAL SYSTEM"),
            Printer._center("TRANSACTION RECEIPT"),
            Printer._line("*"),
            "",
            Printer._line("-"),
            f"  DATE/TIME: {now}",
            f"  TRANSACTION ID: {transaction_id}",
            Printer._line("-"),
            "",
            f"  ACCOUNT HOLDER: {account['first_name']} {account['last_name']}",
            f"  ACCOUNT NUMBER: {account['account_number']}",
            f"  ACCOUNT TYPE: {account['account_type'].upper()}",
            "",
            Printer._line("-"),
            f"  TRANSACTION TYPE: {txn_type}",
            f"  AMOUNT: {currency.format_amount(amount)}",
            "",
            f"  NEW BALANCE: {currency.format_amount(new_balance)}",
            Printer._line("-"),
            "",
        ]

        # Add description only if it exists
        if description:
            lines.extend([
                f"  DESCRIPTION: {description}",
                "",
            ])

        lines.extend([
            Printer._center("Thank you for banking with KIDBANK"),
            Printer._line("*"),
            "",
            "",
        ])

        return "\n".join(lines)

    @staticmethod
    def format_statement(account: Dict, transactions: List[Dict]) -> str:
        """Format an account statement.

        Args:
            account: Account dictionary with holder info, number, balance, currency
            transactions: List of transaction dictionaries

        Returns:
            Formatted statement as string
        """
        currency = get_currency(account["currency"])
        now = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

        lines = [
            "",
            Printer._line("*"),
            Printer._center("KIDBANK TERMINAL SYSTEM"),
            Printer._center("ACCOUNT STATEMENT"),
            Printer._line("*"),
            "",
            f"  STATEMENT DATE: {now}",
            "",
            Printer._line("-"),
            f"  ACCOUNT HOLDER: {account['first_name']} {account['last_name']}",
            f"  ACCOUNT NUMBER: {account['account_number']}",
            f"  ACCOUNT TYPE: {account['account_type'].upper()}",
            f"  CURRENCY: {currency.name}",
            "",
            f"  CURRENT BALANCE: {currency.format_amount(account['balance'])}",
            Printer._line("-"),
            "",
            Printer._center("RECENT TRANSACTIONS"),
            "",
        ]

        if not transactions:
            lines.append(Printer._center("No transactions on record"))
        else:
            # Header
            lines.append("  DATE/TIME           TYPE          AMOUNT              BALANCE")
            lines.append(Printer._line("-"))

            # Transactions
            for txn in transactions:
                date_str = Printer._format_datetime(txn["created_at"])
                txn_type = txn["transaction_type"].upper()[:10]
                amount = currency.format_amount(txn["amount"])
                balance = currency.format_amount(txn["balance_after"])
                sign = "+" if txn_type.startswith("DEPOSIT") else "-"

                # Format line with proper spacing
                line = f"  {date_str:20s} {txn_type:10s} {sign}{amount:>15s}  {balance:>15s}"
                lines.append(line)

        lines.extend([
            "",
            Printer._line("*"),
            Printer._center("Thank you for banking with KIDBANK"),
            Printer._line("*"),
            "",
            "",
        ])

        return "\n".join(lines)

    @staticmethod
    def format_detailed_statement(account: Dict, transactions: List[Dict]) -> str:
        """Format a detailed account statement with transaction notes.

        Args:
            account: Account dictionary with holder info, number, balance, currency
            transactions: List of transaction dictionaries

        Returns:
            Formatted detailed statement as string
        """
        currency = get_currency(account["currency"])
        now = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

        lines = [
            "",
            Printer._line("*"),
            Printer._center("KIDBANK TERMINAL SYSTEM"),
            Printer._center("DETAILED ACCOUNT STATEMENT"),
            Printer._line("*"),
            "",
            f"  STATEMENT DATE: {now}",
            "",
            Printer._line("-"),
            f"  ACCOUNT HOLDER: {account['first_name']} {account['last_name']}",
            f"  ACCOUNT NUMBER: {account['account_number']}",
            f"  ACCOUNT TYPE: {account['account_type'].upper()}",
            f"  CURRENCY: {currency.name}",
            "",
            f"  CURRENT BALANCE: {currency.format_amount(account['balance'])}",
            Printer._line("-"),
            "",
            Printer._center("TRANSACTION DETAILS"),
            "",
        ]

        if not transactions:
            lines.append(Printer._center("No transactions on record"))
        else:
            # Show each transaction with full details
            for i, txn in enumerate(transactions, 1):
                date_str = Printer._format_datetime(txn["created_at"])
                txn_type = txn["transaction_type"].upper()
                amount = currency.format_amount(txn["amount"])
                balance = currency.format_amount(txn["balance_after"])
                sign = "+" if txn_type.startswith("DEPOSIT") else "-"
                description = txn.get("description", "")

                lines.append(Printer._line("-"))
                lines.append(f"  TRANSACTION #{i}")
                lines.append(f"  Date/Time: {date_str}")
                lines.append(f"  Type: {txn_type}")
                lines.append(f"  Amount: {sign}{amount}")
                lines.append(f"  Balance After: {balance}")

                if description:
                    lines.append(f"  Notes: {description}")

                lines.append("")

        lines.extend([
            Printer._line("*"),
            Printer._center("Thank you for banking with KIDBANK"),
            Printer._line("*"),
            "",
            "",
        ])

        return "\n".join(lines)

    @staticmethod
    def print_document(content: str) -> None:
        """Send document to default printer using lp command.

        Args:
            content: Text content to print

        Raises:
            PrinterError: If printing fails
        """
        try:
            # Use lp command to print to default printer
            result = subprocess.run(
                ["lp"],
                input=content.encode("utf-8"),
                capture_output=True,
                timeout=10
            )

            if result.returncode != 0:
                error_msg = result.stderr.decode("utf-8").strip()
                raise PrinterError(f"Print failed: {error_msg}")

        except subprocess.TimeoutExpired:
            raise PrinterError("Print command timed out")
        except FileNotFoundError:
            raise PrinterError("lp command not found. Ensure CUPS is installed.")
        except Exception as e:
            raise PrinterError(f"Print error: {str(e)}")

    @classmethod
    def print_receipt(cls, account: Dict, transaction: Dict, transaction_id: int) -> None:
        """Print a transaction receipt.

        Args:
            account: Account dictionary
            transaction: Transaction dictionary
            transaction_id: Transaction ID

        Raises:
            PrinterError: If printing fails
        """
        content = cls.format_receipt(account, transaction, transaction_id)
        cls.print_document(content)

    @classmethod
    def print_statement(cls, account: Dict, transactions: List[Dict]) -> None:
        """Print an account statement.

        Args:
            account: Account dictionary
            transactions: List of transaction dictionaries

        Raises:
            PrinterError: If printing fails
        """
        content = cls.format_statement(account, transactions)
        cls.print_document(content)

    @classmethod
    def print_detailed_statement(cls, account: Dict, transactions: List[Dict]) -> None:
        """Print a detailed account statement with transaction notes.

        Args:
            account: Account dictionary
            transactions: List of transaction dictionaries

        Raises:
            PrinterError: If printing fails
        """
        content = cls.format_detailed_statement(account, transactions)
        cls.print_document(content)
