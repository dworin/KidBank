"""Currency configuration and formatting."""

from typing import Dict, List


class Currency:
    """Represents a currency with its display properties."""

    def __init__(self, code: str, name: str, symbol: str):
        """Initialize currency.

        Args:
            code: Currency code (e.g., 'USD', 'BB')
            name: Full currency name (e.g., 'US Dollars')
            symbol: Display symbol (e.g., '$', 'BB')
        """
        self.code = code
        self.name = name
        self.symbol = symbol

    def format_amount(self, amount: float) -> str:
        """Format an amount with this currency.

        Args:
            amount: The amount to format

        Returns:
            Formatted string (e.g., '$1,000.00' or '1,000.00 BB')
        """
        if self.code == "USD":
            return f"{self.symbol}{amount:,.2f}"
        else:
            # For other currencies, put symbol after
            return f"{amount:,.2f} {self.symbol}"


# Define available currencies
CURRENCIES: Dict[str, Currency] = {
    "USD": Currency("USD", "US Dollars", "$"),
    "BB": Currency("BB", "BrainBucks", "BB"),
}


def get_currency(code: str) -> Currency:
    """Get a currency by its code.

    Args:
        code: Currency code

    Returns:
        Currency object

    Raises:
        ValueError: If currency code is not found
    """
    if code not in CURRENCIES:
        raise ValueError(f"Unknown currency: {code}")
    return CURRENCIES[code]


def get_available_currencies() -> List[Currency]:
    """Get list of all available currencies.

    Returns:
        List of Currency objects
    """
    return list(CURRENCIES.values())


def is_valid_currency(code: str) -> bool:
    """Check if a currency code is valid.

    Args:
        code: Currency code to check

    Returns:
        True if valid, False otherwise
    """
    return code in CURRENCIES
