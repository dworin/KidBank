# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kidbank is a local terminal-based banking application that replicates the text-based user interface of bank teller terminals from the 1980s-1990s. It's designed for managing checking and savings accounts with a retro, keystroke-driven interface.

## Technical Stack

- **Language**: Python 3.8+
- **UI Framework**: Textual (modern TUI framework for retro terminal aesthetic)
- **Data Storage**: SQLite database via Python's built-in `sqlite3` module
- **Core Features**: Account creation, deposits, withdrawals

## Commands

### Setup

**First Time Setup:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (Linux/macOS)
source .venv/bin/activate

# Activate virtual environment (Windows)
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

**Subsequent Sessions:**
```bash
# Just activate the virtual environment
source .venv/bin/activate
```

### Running the Application
```bash
# Make sure venv is activated first!
python kidbank.py
```

### Development
```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_database.py

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
kidbank/
├── src/kidbank/          # Main application code
│   ├── __init__.py
│   ├── app.py           # Textual app and UI components
│   └── database.py      # SQLite database management
├── tests/               # Test files
├── kidbank.py           # Entry point script
└── requirements.txt     # Production dependencies
```

## Architecture Notes

**Database Layer** (`database.py`): The `Database` class manages SQLite connections and schema initialization. Data is stored in `~/.kidbank/kidbank.db` by default with two main tables:
- `accounts`: Stores account information (account_number, account_type, balance)
- `transactions`: Records all transactions with references to accounts

**UI Layer** (`app.py`): Built with Textual framework, which provides a modern way to create retro-styled terminal interfaces. The `KidbankApp` class extends `textual.app.App` and manages screen composition and key bindings.

**Principles**:
- All operations are local-only with no network connectivity
- Retro terminal aesthetic with keyboard-driven navigation
- SQLite provides ACID compliance for transaction safety
