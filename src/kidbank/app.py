"""Main application class for Kidbank."""

from typing import Dict
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Static, Button, Input, Label, ListView, ListItem
from textual.binding import Binding

from .database import Database
from .accounts import AccountManager
from .currency import get_currency, get_available_currencies
from .printer import Printer, PrinterError


class MainMenuScreen(Screen):
    """Main menu showing list of accounts."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "new_account", "New Account"),
    ]

    def __init__(self, account_manager: AccountManager):
        super().__init__()
        self.account_manager = account_manager

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield Container(
            Static("KIDBANK TERMINAL SYSTEM v1.0", id="title"),
            Static("═" * 60, id="divider"),
            ListView(id="account_list"),
            Static("\n[N] New Account  [Q] Quit", id="menu_help"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load accounts when screen is mounted."""
        self.refresh_account_list()

    def refresh_account_list(self, result=None) -> None:
        """Refresh the account list."""
        list_view = self.query_one("#account_list", ListView)
        list_view.clear()

        accounts = self.account_manager.list_accounts()

        if not accounts:
            list_view.append(ListItem(Label("No accounts found. Press [N] to create one.")))
        else:
            for account in accounts:
                name = f"{account['first_name']} {account['last_name']}"
                acct_num = account['account_number']
                acct_type = account["account_type"].upper()
                currency = get_currency(account["currency"])
                balance_str = currency.format_amount(account["balance"])
                label = f"{acct_num}  {name:25s}  {acct_type:10s}  {balance_str}"
                list_view.append(ListItem(Label(label), name=account["account_number"]))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle account selection."""
        if event.item.name:  # Has an account number
            self.app.push_screen(
                AccountDetailScreen(self.account_manager, event.item.name),
                callback=self.refresh_account_list
            )

    def action_new_account(self) -> None:
        """Open new account creation screen."""
        self.app.push_screen(CreateAccountScreen(self.account_manager), callback=self.refresh_account_list)


class AccountDetailScreen(Screen):
    """Screen showing account details and transactions."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("d", "deposit", "Deposit"),
        ("w", "withdraw", "Withdraw"),
        ("p", "print_statement", "Print Statement"),
    ]

    def __init__(self, account_manager: AccountManager, account_number: str):
        super().__init__()
        self.account_manager = account_manager
        self.account_number = account_number

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield Container(
            Static(id="account_info"),
            Static("═" * 60, id="divider"),
            Static("RECENT TRANSACTIONS:", id="transactions_header"),
            ListView(id="transaction_list"),
            Static("\n[D] Deposit  [W] Withdraw  [P] Print Statement  [ESC] Back", id="detail_help"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load account details when screen is mounted."""
        self.refresh_details()

    def refresh_details(self, result=None) -> None:
        """Refresh account details and transactions."""
        account = self.account_manager.get_account(self.account_number)
        if not account:
            self.app.pop_screen()
            return

        # Update account info
        info_widget = self.query_one("#account_info", Static)
        name = f"{account['first_name']} {account['last_name']}"
        acct_type = account["account_type"].upper()
        currency = get_currency(account["currency"])
        balance_str = currency.format_amount(account["balance"])
        info_widget.update(
            f"Account Holder: {name}\n"
            f"Account: {account['account_number']}  Type: {acct_type}  Currency: {currency.name}\n"
            f"Balance: {balance_str}"
        )

        # Update transaction list
        list_view = self.query_one("#transaction_list", ListView)
        list_view.clear()

        transactions = self.account_manager.get_transactions(self.account_number, limit=10)

        if not transactions:
            list_view.append(ListItem(Label("No transactions")))
        else:
            for txn in transactions:
                txn_type = txn["transaction_type"].upper()
                amount_str = currency.format_amount(txn["amount"])
                balance_str = currency.format_amount(txn["balance_after"])
                date = txn["created_at"][:19]  # Trim microseconds
                sign = "+" if txn_type == "DEPOSIT" else "-"
                label = f"{date}  {txn_type:12s}  {sign}{amount_str}  Bal: {balance_str}"
                list_view.append(ListItem(Label(label)))

    def action_deposit(self) -> None:
        """Open deposit form."""
        self.app.push_screen(
            TransactionScreen(self.account_manager, self.account_number, "deposit"),
            callback=self.refresh_details
        )

    def action_withdraw(self) -> None:
        """Open withdrawal form."""
        self.app.push_screen(
            TransactionScreen(self.account_manager, self.account_number, "withdrawal"),
            callback=self.refresh_details
        )

    def action_print_statement(self) -> None:
        """Print account statement."""
        account = self.account_manager.get_account(self.account_number)
        if not account:
            return

        transactions = self.account_manager.get_transactions(self.account_number, limit=20)

        try:
            Printer.print_statement(account, transactions)
            # Show success message
            self.app.push_screen(MessageScreen("Statement sent to printer successfully!"))
        except PrinterError as e:
            # Show error message
            self.app.push_screen(MessageScreen(f"Print failed: {str(e)}", is_error=True))

    def action_back(self) -> None:
        """Return to main menu."""
        self.dismiss(None)


class MessageScreen(Screen):
    """Simple screen to display a message."""

    BINDINGS = [
        ("escape", "back", "Close"),
        ("enter", "back", "Close"),
    ]

    def __init__(self, message: str, is_error: bool = False):
        super().__init__()
        self.message = message
        self.is_error = is_error

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        title = "ERROR" if self.is_error else "SUCCESS"
        yield Header()
        yield Container(
            Static(title, id="title"),
            Static("═" * 60, id="divider"),
            Static(self.message, id="message_content"),
            Static(""),
            Button("Close", id="btn_close", variant="primary"),
            Static("\n[ENTER] or [ESC] to close", id="message_help"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle close button."""
        if event.button.id == "btn_close":
            self.dismiss(None)

    def action_back(self) -> None:
        """Close the message screen."""
        self.dismiss(None)


class CreateAccountScreen(Screen):
    """Screen for creating a new account."""

    BINDINGS = [
        ("escape", "back", "Cancel"),
    ]

    def __init__(self, account_manager: AccountManager):
        super().__init__()
        self.account_manager = account_manager

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Build currency buttons dynamically
        currencies = get_available_currencies()
        currency_buttons = [
            Button(curr.name, id=f"btn_currency_{curr.code}", variant="primary")
            for curr in currencies
        ]

        yield Header()
        yield VerticalScroll(
            Static("CREATE NEW ACCOUNT", id="title"),
            Static("═" * 60, id="divider"),
            Static(""),
            Label("First Name:"),
            Input(placeholder="First name", id="first_name"),
            Static(""),
            Label("Last Name:"),
            Input(placeholder="Last name", id="last_name"),
            Static(""),
            Label("Account Type:"),
            Horizontal(
                Button("Checking", id="btn_checking", variant="primary"),
                Button("Savings", id="btn_savings", variant="primary"),
                id="account_type_buttons",
            ),
            Static(""),
            Label("Currency:"),
            Horizontal(*currency_buttons, id="currency_buttons"),
            Static(""),
            Label("Initial Deposit:"),
            Input(placeholder="0.00", id="initial_deposit"),
            Static(""),
            Button("Create Account", id="btn_create", variant="success"),
            Static(""),
            Static("[ESC] Cancel", id="create_help"),
            Static(id="error_message"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus on first button when mounted."""
        self.selected_type = None
        self.selected_currency = None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn_checking":
            self.selected_type = "checking"
            self.query_one("#btn_checking", Button).variant = "success"
            self.query_one("#btn_savings", Button).variant = "primary"
        elif event.button.id == "btn_savings":
            self.selected_type = "savings"
            self.query_one("#btn_checking", Button).variant = "primary"
            self.query_one("#btn_savings", Button).variant = "success"
        elif event.button.id.startswith("btn_currency_"):
            # Extract currency code from button id
            currency_code = event.button.id.replace("btn_currency_", "")
            self.selected_currency = currency_code
            # Update all currency buttons
            for curr in get_available_currencies():
                btn_id = f"btn_currency_{curr.code}"
                try:
                    btn = self.query_one(f"#{btn_id}", Button)
                    btn.variant = "success" if curr.code == currency_code else "primary"
                except:
                    pass
        elif event.button.id == "btn_create":
            self.create_account()

    def create_account(self) -> None:
        """Create the account."""
        error_widget = self.query_one("#error_message", Static)

        if not self.selected_type:
            error_widget.update("Error: Please select account type")
            return

        if not self.selected_currency:
            error_widget.update("Error: Please select currency")
            return

        try:
            first_name = self.query_one("#first_name", Input).value.strip()
            last_name = self.query_one("#last_name", Input).value.strip()
            deposit_input = self.query_one("#initial_deposit", Input).value.strip()
            initial_deposit = float(deposit_input) if deposit_input else 0.0

            if initial_deposit < 0:
                error_widget.update("Error: Initial deposit cannot be negative")
                return

            account = self.account_manager.create_account(
                first_name, last_name, self.selected_type, self.selected_currency, initial_deposit
            )
            self.dismiss(account)

        except ValueError as e:
            error_widget.update(f"Error: {str(e)}")

    def action_back(self) -> None:
        """Cancel and return to main menu."""
        self.dismiss(None)


class TransactionConfirmationScreen(Screen):
    """Screen shown after successful transaction with print option."""

    BINDINGS = [
        ("escape", "back", "Continue"),
        ("enter", "back", "Continue"),
    ]

    def __init__(self, account_manager: AccountManager, account_number: str,
                 transaction: Dict, transaction_id: int):
        super().__init__()
        self.account_manager = account_manager
        self.account_number = account_number
        self.transaction = transaction
        self.transaction_id = transaction_id

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        account = self.account_manager.get_account(self.account_number)
        currency = get_currency(account["currency"])

        txn_type = self.transaction["transaction_type"].upper()
        amount = currency.format_amount(self.transaction["amount"])
        new_balance = currency.format_amount(self.transaction["new_balance"])

        yield Header()
        yield Container(
            Static("TRANSACTION SUCCESSFUL", id="title"),
            Static("═" * 60, id="divider"),
            Static(f"\n{txn_type}: {amount}", id="transaction_summary"),
            Static(f"New Balance: {new_balance}\n", id="balance_info"),
            Horizontal(
                Button("Print Receipt", id="btn_print", variant="success"),
                Button("Continue", id="btn_continue", variant="primary"),
                id="confirmation_buttons",
            ),
            Static("\n[ENTER] or [ESC] to continue without printing", id="confirmation_help"),
            Static(id="print_error"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn_print":
            self.print_receipt()
        elif event.button.id == "btn_continue":
            self.dismiss(None)

    def print_receipt(self) -> None:
        """Print the transaction receipt."""
        account = self.account_manager.get_account(self.account_number)
        if not account:
            return

        try:
            Printer.print_receipt(account, self.transaction, self.transaction_id)
            # Show success and close after a moment
            error_widget = self.query_one("#print_error", Static)
            error_widget.update("Receipt sent to printer!")
            # Auto-close after showing message
            self.set_timer(1.5, lambda: self.dismiss(None))
        except PrinterError as e:
            # Show error message
            error_widget = self.query_one("#print_error", Static)
            error_widget.update(f"Print failed: {str(e)}")

    def action_back(self) -> None:
        """Continue without printing."""
        self.dismiss(None)


class TransactionScreen(Screen):
    """Screen for making deposits or withdrawals."""

    BINDINGS = [
        ("escape", "back", "Cancel"),
    ]

    def __init__(self, account_manager: AccountManager, account_number: str, transaction_type: str):
        super().__init__()
        self.account_manager = account_manager
        self.account_number = account_number
        self.transaction_type = transaction_type

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        title = "DEPOSIT" if self.transaction_type == "deposit" else "WITHDRAWAL"

        # Get account info for currency display
        account = self.account_manager.get_account(self.account_number)
        if account:
            currency = get_currency(account["currency"])
            amount_label = f"\nAmount ({currency.symbol}):"
        else:
            amount_label = "\nAmount:"

        yield Header()
        yield Container(
            Static(title, id="title"),
            Static("═" * 60, id="divider"),
            Static(f"Account: {self.account_number}", id="account_info"),
            Vertical(
                Label(amount_label),
                Input(placeholder="0.00", id="amount"),
                Label("\nDescription (optional):"),
                Input(placeholder="Transaction description", id="description"),
                Static(""),
                Button(f"Submit {title.capitalize()}", id="btn_submit", variant="success"),
                Static("\n[ESC] Cancel", id="transaction_help"),
                id="form_container",
            ),
            Static(id="error_message"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus on amount input when mounted."""
        self.query_one("#amount", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle submit button."""
        if event.button.id == "btn_submit":
            self.submit_transaction()

    def submit_transaction(self) -> None:
        """Submit the transaction."""
        error_widget = self.query_one("#error_message", Static)

        try:
            amount_input = self.query_one("#amount", Input).value.strip()
            if not amount_input:
                error_widget.update("Error: Please enter an amount")
                return

            amount = float(amount_input)
            description = self.query_one("#description", Input).value.strip()

            if self.transaction_type == "deposit":
                result = self.account_manager.deposit(self.account_number, amount, description)
            else:
                result = self.account_manager.withdraw(self.account_number, amount, description)

            # Show confirmation screen with print option
            transaction_id = result.get("transaction_id")
            self.app.push_screen(
                TransactionConfirmationScreen(
                    self.account_manager,
                    self.account_number,
                    result,
                    transaction_id
                ),
                callback=lambda _: self.dismiss(result)
            )

        except ValueError as e:
            error_widget.update(f"Error: {str(e)}")

    def action_back(self) -> None:
        """Cancel and return to account details."""
        self.dismiss(None)


class KidbankApp(App):
    """A retro terminal-based banking application."""

    CSS = """
    Screen {
        background: $surface;
    }

    #title {
        text-style: bold;
        padding: 1;
        content-align: center middle;
    }

    #divider {
        color: $text-muted;
        padding: 0 1;
    }

    #account_list {
        height: 1fr;
        margin: 1;
    }

    #transaction_list {
        height: 1fr;
        margin: 1;
    }

    #menu_help, #detail_help, #create_help, #transaction_help, #message_help, #confirmation_help {
        color: $text-muted;
        padding: 1;
    }

    #message_content, #transaction_summary, #balance_info {
        padding: 1 2;
    }

    #confirmation_buttons {
        padding: 1;
        height: auto;
    }

    #print_error {
        color: $success;
        padding: 1 2;
    }

    #form_container {
        padding: 1 2;
        height: auto;
    }

    #error_message {
        color: $error;
        padding: 1 2;
    }

    Horizontal {
        height: auto;
        width: 100%;
    }

    Button {
        margin: 1 1;
        min-width: 16;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.account_manager = AccountManager(self.db)

    def on_mount(self) -> None:
        """Initialize the database and push main menu."""
        self.db.connect()
        self.push_screen(MainMenuScreen(self.account_manager))

    def on_unmount(self) -> None:
        """Close database connection when app closes."""
        self.db.close()


if __name__ == "__main__":
    app = KidbankApp()
    app.run()
