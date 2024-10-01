# SensibullQuotes

SensibullQuotes is a Python package that provides an interface to fetch and process live derivative prices and quotes from Sensibull's API.

## Features

- Fetch derivatives data including instrument tokens and trading symbols
- Get live derivative prices for a given instrument token
- Get quotes for one or multiple trading symbols
- Process and clean up the live derivative data for easy consumption

## Installation

You can install SensibullQuotes using pip:
pip install sensibull-quotes
Copy
## Usage

Here's a basic example of how to use SensibullQuotes:

```python
from sensibull_quotes import SensibullQuotes

# Create an instance of SensibullQuotes
quotes = SensibullQuotes()

# Fetch derivatives data (this is done automatically when needed, but you can do it explicitly)
quotes.fetch_derivatives_data()

# Get a trading symbol for an instrument token
symbol = quotes.get_tradingsymbol(9073154)
print(f"Trading Symbol: {symbol}")

# Get quotes for a single trading symbol
single_quote = quotes.get_quotes('NIFTY')
print(f"NIFTY Quote: {single_quote}")

# Get quotes for multiple trading symbols
multiple_quotes = quotes.get_quotes(['NIFTY', 'BANKNIFTY', 'FINNIFTY'])
for symbol, quote in multiple_quotes.items():
    print(f"{symbol} Quote: {quote}")

# Get live derivative prices for an instrument token
live_data = quotes.get_live_derivative_prices(260105)

if live_data:
    print(f"Underlying Price: {live_data['underlying_price']}")
    print(f"Last Updated: {live_data['last_updated_at']}")
    for expiry in live_data['expiries']:
        print(f"\nExpiry: {expiry['expiry']}")
        print(f"ATM Strike: {expiry['atm_strike']}")
        print(f"ATM IV: {expiry['atm_iv']}")
        print(f"Future Price: {expiry['future_price']}")
        print(f"Max OI: {expiry['max_oi']}")
        print("Options:")
        for option in expiry['options']:
            print(f"  Token: {option['token']}, Trading Symbol: {option['tradingsymbol']}, Last Price: {option['last_price']}, OI: {option['oi']}, IV: {option['iv']}")
else:
    print("Failed to fetch live derivative prices")
API Reference
SensibullQuotes
The main class that provides access to Sensibull's API.
Methods:

fetch_derivatives_data(max_retries=3): Fetches the derivatives data from Sensibull's API.
get_tradingsymbol(instrument_token): Returns the trading symbol for a given instrument token.
get_live_derivative_prices(instrument_token): Fetches and processes live derivative prices for a given instrument token.
get_quotes(trading_symbols): Fetches quotes for one or more trading symbols.

trading_symbols: A string (for a single symbol) or a list of strings (for multiple symbols)
Returns a dictionary where keys are trading symbols and values are quote information



Quote Information
The get_quotes method returns a dictionary with the following information for each quote:

last_price: The last traded price
instrument_token: The unique identifier for the instrument
underlying_instrument: The underlying instrument (e.g., NIFTY for NIFTY options)
tradingsymbol: The trading symbol
segment: The market segment (e.g., NSE, NFO)
exchange: The exchange (e.g., NSE)
instrument_type: The type of instrument (e.g., EQ for equity, CE for call option)
last_updated_at: The timestamp of the last update
strike: The strike price (for options)
expiry: The expiry date (for derivatives)
oi: Open Interest
volume: Trading volume

Note that some fields may be None if not applicable or not available for a particular instrument.
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
License
This project is licensed under the MIT License.
Disclaimer
This package is not officially associated with or endorsed by Sensibull. Use at your own risk.

