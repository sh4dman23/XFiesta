import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps

from math import trunc

# Max number of digits in card
N = 16


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(
            url,
            cookies={"session": str(uuid.uuid4())},
            headers={"User-Agent": "python-requests", "Accept": "*/*"},
        )
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        quotes.reverse()
        price = round(float(quotes[0]["Adj Close"]), 2)
        return {"name": symbol, "price": price, "symbol": symbol}
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


# Check the credit card number using Luhn's Algorithm
def check_card(number):
    if not (number >= 1e12 and number < 1e13) and not (
        number >= 1e14 and number < 1e16
    ):
        return False

    def checkl(number):
        sum1 = 0
        sum2 = 0

        for i in range(N):
            digit = number % 10

            if i % 2 == 0:
                sum1 += digit
            else:
                sum2 += (2 * digit) % 10 + trunc(2 * digit / 10)

            number = trunc(number / 10)

        if (sum1 + sum2) % 10 == 0:
            return True
        return False

    # Check for VISA
    if (
        (number >= 4e12 and number < 5e12) or (number >= 4e15 and number < 5e15)
    ) and checkl(number):
        return True

    # Check for AMEX
    elif (
        (number >= 3.4e14 and number < 3.5e14) or (number >= 3.7e14 and number < 3.8e14)
    ) and checkl(number):
        return True

    # Check for MASTERCARD
    elif (number >= 5.1e15 and number < 5.6e15) and checkl(number):
        return True
    else:
        return False
