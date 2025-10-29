"""Tests for printer functionality."""

import pytest
from unittest.mock import patch, MagicMock
from src.kidbank.printer import Printer, PrinterError


class TestPrinterFormatting:
    """Test receipt and statement formatting."""

    def test_format_receipt(self):
        """Test receipt formatting."""
        account = {
            "first_name": "John",
            "last_name": "Doe",
            "account_number": "123456",
            "account_type": "checking",
            "currency": "USD",
            "balance": 1000.00
        }

        transaction = {
            "transaction_type": "deposit",
            "amount": 100.00,
            "new_balance": 1000.00,
            "description": "Test deposit"
        }

        receipt = Printer.format_receipt(account, transaction, 42)

        assert "KIDBANK TERMINAL SYSTEM" in receipt
        assert "TRANSACTION RECEIPT" in receipt
        assert "John Doe" in receipt
        assert "123456" in receipt
        assert "DEPOSIT" in receipt
        assert "$100.00" in receipt
        assert "$1,000.00" in receipt
        assert "Test deposit" in receipt
        assert "TRANSACTION ID: 42" in receipt

    def test_format_statement(self):
        """Test statement formatting."""
        account = {
            "first_name": "Jane",
            "last_name": "Smith",
            "account_number": "789012",
            "account_type": "savings",
            "currency": "USD",
            "balance": 5000.50
        }

        transactions = [
            {
                "transaction_type": "deposit",
                "amount": 1000.00,
                "balance_after": 5000.50,
                "created_at": "2025-10-28 10:00:00"
            },
            {
                "transaction_type": "withdrawal",
                "amount": 200.00,
                "balance_after": 4000.50,
                "created_at": "2025-10-27 15:30:00"
            }
        ]

        statement = Printer.format_statement(account, transactions)

        assert "KIDBANK TERMINAL SYSTEM" in statement
        assert "ACCOUNT STATEMENT" in statement
        assert "Jane Smith" in statement
        assert "789012" in statement
        assert "SAVINGS" in statement
        assert "$5,000.50" in statement
        assert "RECENT TRANSACTIONS" in statement
        assert "$1,000.00" in statement
        assert "$200.00" in statement

    def test_format_statement_no_transactions(self):
        """Test statement formatting with no transactions."""
        account = {
            "first_name": "Empty",
            "last_name": "Account",
            "account_number": "000000",
            "account_type": "checking",
            "currency": "USD",
            "balance": 0.00
        }

        statement = Printer.format_statement(account, [])

        assert "ACCOUNT STATEMENT" in statement
        assert "Empty Account" in statement
        assert "No transactions on record" in statement


class TestPrinterPrinting:
    """Test actual printing functionality."""

    @patch('subprocess.run')
    def test_print_document_success(self, mock_run):
        """Test successful print."""
        mock_run.return_value = MagicMock(returncode=0, stderr=b"")

        # Should not raise
        Printer.print_document("Test content")

        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["lp"]

    @patch('subprocess.run')
    def test_print_document_failure(self, mock_run):
        """Test print failure."""
        mock_run.return_value = MagicMock(returncode=1, stderr=b"Printer error")

        with pytest.raises(PrinterError) as exc_info:
            Printer.print_document("Test content")

        assert "Print failed: Printer error" in str(exc_info.value)

    @patch('subprocess.run')
    def test_print_receipt(self, mock_run):
        """Test print receipt wrapper."""
        mock_run.return_value = MagicMock(returncode=0, stderr=b"")

        account = {
            "first_name": "Test",
            "last_name": "User",
            "account_number": "111111",
            "account_type": "checking",
            "currency": "USD",
            "balance": 100.00
        }

        transaction = {
            "transaction_type": "deposit",
            "amount": 50.00,
            "new_balance": 100.00,
            "description": "Test"
        }

        Printer.print_receipt(account, transaction, 1)

        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_print_statement(self, mock_run):
        """Test print statement wrapper."""
        mock_run.return_value = MagicMock(returncode=0, stderr=b"")

        account = {
            "first_name": "Test",
            "last_name": "User",
            "account_number": "111111",
            "account_type": "checking",
            "currency": "USD",
            "balance": 100.00
        }

        transactions = []

        Printer.print_statement(account, transactions)

        mock_run.assert_called_once()
