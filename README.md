# Kidbank

A retro terminal-based banking application that brings the nostalgic text-based interface of 1980s-1990s bank teller terminals to your command line.

## Overview

Kidbank is a local, offline banking application designed for managing checking and savings accounts with a vintage, keystroke-driven interface. Perfect for educational purposes, personal finance tracking, or anyone who appreciates the simplicity of classic terminal UIs.

## Features

- **Retro Terminal Interface**: Authentic text-based UI reminiscent of classic banking terminals
- **Account Management**: Create and manage checking and savings accounts
- **Basic Transactions**: Support for deposits, withdrawals, and balance inquiries
- **Local Storage**: All data stored securely in a local SQLite database
- **Offline Operation**: No network connectivity required - completely local and private
- **Keyboard-Driven**: Navigate efficiently using keystroke commands

## Tech Stack

- **Python 3.8+**: Core application language
- **Textual**: Modern TUI (Text User Interface) framework for creating the retro terminal aesthetic
- **SQLite**: Lightweight, embedded database for transaction management
- **ACID Compliance**: Reliable transaction processing with SQLite guarantees

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/dworin/KidBank.git
cd KidBank
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
```

3. Activate the virtual environment:
```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure your virtual environment is activated:
```bash
source .venv/bin/activate  # Linux/macOS
```

2. Run the application:
```bash
python kidbank.py
```

3. Navigate using keyboard commands to:
   - Create new accounts
   - Make deposits
   - Process withdrawals
   - Check account balances

## Project Structure

```
kidbank/
├── src/kidbank/          # Main application code
│   ├── __init__.py
│   ├── app.py           # Textual app and UI components
│   ├── accounts.py      # Account management logic
│   ├── currency.py      # Currency handling utilities
│   └── database.py      # SQLite database management
├── tests/               # Test files
├── kidbank.py           # Application entry point
├── requirements.txt     # Production dependencies
└── requirements-dev.txt # Development dependencies
```

## Data Storage

Account and transaction data is stored locally in `~/.kidbank/kidbank.db`. The database contains:
- **accounts** table: Account information (account_number, account_type, balance)
- **transactions** table: Complete transaction history with account references

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/ tests/
```

### Linting
```bash
flake8 src/ tests/
```

### Type Checking
```bash
mypy src/
```

## Design Principles

- **Privacy First**: No network connectivity, all data stays local
- **Retro Aesthetic**: Keyboard-driven navigation with classic terminal styling
- **Transaction Safety**: SQLite ACID compliance ensures data integrity
- **Simplicity**: Focused on core banking operations without unnecessary complexity

## License

This project is open source and available for educational and personal use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve Kidbank.
