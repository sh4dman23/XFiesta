import os

from cs50 import SQL
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, check_card

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = os.getenv("SECRET_KEY") or "b'\xf2F\xff\x9b4\xf1g\xa9\xe7\t\x81&{\xd5\x975\x87\xfb5y>\x0c1\xa1'"

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    stocks = list()
    sum = 0

    # Get net shares for each stock with distinct symbols
    shares_list = db.execute(
        "SELECT symbol, SUM(CASE WHEN t_type = 'Purchase' THEN shares ELSE -shares END) as net_shares FROM transactions WHERE user_id = ? GROUP BY symbol ORDER BY symbol;",
        session["user_id"],
    )

    # Iterate over each stock and add to stock list
    for share in shares_list:
        symbol = share["symbol"]
        net_shares = share["net_shares"]

        # Skip if number of shares is not greater than 0
        if not (net_shares > 0):
            continue

        # Add to stocks
        results = lookup(symbol)
        stock = {
            "symbol": symbol,
            "shares": net_shares,
            "price": usd(results["price"]),
            "total": usd(net_shares * float(results["price"])),
        }
        stocks.append(stock)
        sum += net_shares * float(results["price"])

    # Get user's current balance
    balance = db.execute("SELECT cash FROM users WHERE id = ?;", session["user_id"])

    return render_template(
        "portfolio.html",
        stocks=stocks,
        sum=usd(sum),
        balance=usd(balance[0]["cash"]),
        total=usd(sum + balance[0]["cash"]),
        type=type,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Get input
        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")

        # Make sure input is valid
        if not username or not password1 or not password2:
            return apology("Invalid Submission!")
        if password1 != password2:
            return apology("Passwords do not match!")
        if len(password1) < 8:
            return apology("Password must be at least 8 characters long!")

        # Make sure username is unique
        count = db.execute(
            "SELECT COUNT(username) AS count FROM users WHERE username = ?;", username
        )
        if count[0]["count"] > 0:
            return apology("Username already exists! Please select a unique username!")

        # Hash password
        hash_pass = generate_password_hash(password1)

        # Register to database
        db.execute(
            "INSERT INTO users(username, hash) VALUES(?, ?);", username, hash_pass
        )

        # Redirect to login page
        return redirect("/login")
    elif not session.get("user_id"):
        return render_template("register.html")
    else:
        return apology("You are already logged in!")


@app.route("/profile")
@login_required
def profile():
    username = db.execute(
        "SELECT username FROM users WHERE id = ?;", session["user_id"]
    )
    return render_template("profile.html", username=username[0]["username"])


@app.route("/change_acc", methods=["GET", "POST"])
@login_required
def change_acc():
    if request.method == "POST":
        # Get and check input
        username = request.form.get("username")
        password_old = request.form.get("password_old")
        password_new = request.form.get("password_new")
        password_new2 = request.form.get("password_new2")
        if (
            not username
            or not password_old
            or not password_new
            or not password_new2
            or not (password_new == password_new2)
        ):
            return apology("Invalid Submission!")
        if len(password_new) < 8:
            return apology("Password must be at least 8 characters long!")

        # To check for existing users with submitted username
        user_count = db.execute(
            "SELECT COUNT(*) AS count FROM users WHERE username = ?", username
        )

        user_old = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # If user exists with new username and new username is not equal to old username
        if user_count[0] and username != user_old[0]["username"]:
            if user_count[0]["count"] > 0:
                return apology("Username already exists!", 403)

        # If old password is incorrect
        if not check_password_hash(user_old[0]["hash"], password_old):
            return apology("invalid username and/or password!", 403)

        # Update user info
        db.execute(
            "UPDATE users SET username = ?, hash = ? WHERE id = ?;",
            username,
            generate_password_hash(password_new),
            session["user_id"],
        )
        return redirect("/profile")

    else:
        username = db.execute(
            "SELECT username FROM users WHERE id = ?;", session["user_id"]
        )
        return render_template("change_acc.html", username=username[0]["username"])


@app.route("/check_username")
def check_username():
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        username = request.args.get("username")
        user_count = db.execute(
            "SELECT COUNT(*) AS count FROM users WHERE username = ?", username
        )
        if user_count[0]:
            if user_count[0]["count"] > 0:
                return jsonify({"result": False})
            else:
                return jsonify({"result": True})
    else:
        return redirect("/")


@app.route("/acc_credit", methods=["GET", "POST"])
@login_required
def acc_credit():
    if request.method == "POST":
        credit_card = request.form.get("credit_card")
        numCredits = request.form.get("numCredits")
        numCvv = str(request.form.get("numCvv"))

        if (
            not credit_card
            or not numCredits
            or not numCvv
            or not numCredits.isdigit()
            or not numCvv.isdigit()
            or (not len(numCvv) == 3 and not len(numCvv) == 4)
            or int(numCredits) < 0
        ):
            return apology("Invalid Submission")
        try:
            credit_card = int(credit_card.replace("-", ""))
        except ValueError:
            return apology("Invalid Credit Card")

        if credit_card < 0 or not check_card(credit_card):
            return apology("Invalid Credit Card")

        db.execute(
            "UPDATE users SET cash = cash + ? WHERE id = ?;",
            int(numCredits),
            session["user_id"],
        )
        return redirect("/")
    else:
        user = db.execute(
            "SELECT username, cash FROM users WHERE id = ?;", session["user_id"]
        )
        years = [year for year in range(2023, 2031)]
        return render_template(
            "acc_credit.html",
            username=user[0]["username"],
            current_credit=usd(user[0]["cash"]),
            years=years,
        )


@app.route("/delete_acc", methods=["GET", "POST"])
@login_required
def delete_acc():
    if request.method == "POST":
        if request.form.get("confirm") == "yes":
            db.execute(
                "DELETE FROM transactions WHERE user_id = ?;", session["user_id"]
            )
            db.execute("DELETE FROM users WHERE id = ?;", session["user_id"])
            session.clear()
            return redirect("/login")
        else:
            return redirect("/profile")
    else:
        return render_template("delete_acc.html")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        results = lookup(symbol)
        if not results:
            return apology("Invalid Symbol!")
        else:
            return render_template(
                "quoted.html", symbol=results["symbol"], price=usd(results["price"])
            )

    else:
        return render_template("quote.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        symbol = symbol.upper()
        shares = request.form.get("shares")

        # Check inpute
        if not symbol or not shares or not shares.isdigit() or int(shares) < 0:
            return apology("Invalid Submission!")

        # Lookup for symbol
        results = lookup(symbol)

        # Check results
        if not results:
            return apology("Invalid Symbol!")
        shares = int(shares)

        # Check and change user balance
        balance_db = db.execute(
            "SELECT cash FROM users WHERE id = ?;", session["user_id"]
        )
        balance = balance_db[0]["cash"]
        total_cost = shares * float(results["price"])
        if balance < total_cost:
            return apology("Insufficient Balance!")
        else:
            db.execute(
                "UPDATE users SET cash = cash - ? WHERE id = ?;",
                total_cost,
                session["user_id"],
            )
        if shares > 0:
            # Add purchase to history
            db.execute(
                "INSERT INTO transactions(user_id, symbol, shares, t_time, t_type, t_price) VALUES(?, ?, ?, CURRENT_TIMESTAMP, 'Purchase', ?);",
                session["user_id"],
                symbol,
                shares,
                results["price"],
            )
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Get and check input
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol or not shares.isdigit() or int(shares) < 0:
            return apology("Invalid Submission!")
        results = lookup(symbol)
        if not results:
            return apology("Invalid Submission!")
        shares = int(shares)

        # Check current amount of stocks
        net_shares = db.execute(
            "SELECT SUM(CASE WHEN t_type = 'Purchase' THEN shares ELSE -shares END) as net_shares FROM transactions WHERE user_id = ? AND symbol = ?;",
            session["user_id"],
            symbol,
        )
        if shares > net_shares[0]["net_shares"]:
            return apology(
                "Number of shares to be sold exceeds number of shares in inventory!"
            )

        # Update user balance and transaction history
        if shares > 0:
            increment = shares * results["price"]
            db.execute(
                "UPDATE users SET cash = cash + ? WHERE id = ?;",
                increment,
                session["user_id"],
            )
            db.execute(
                "INSERT INTO transactions (user_id, symbol, shares, t_time, t_type, t_price) VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'Sale', ?);",
                session["user_id"],
                symbol.upper(),
                shares,
                results["price"],
            )
        return redirect("/")

    else:
        stocks = db.execute(
            "SELECT symbol, SUM(CASE WHEN t_type = 'Purchase' THEN shares ELSE -shares END) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol ORDER BY symbol;",
            session["user_id"],
        )
        return render_template("sell.html", stocks=stocks)


@app.route("/history")
@login_required
def history():
    stock_history = db.execute(
        "SELECT symbol, shares, t_time, t_type, t_price FROM transactions WHERE user_id = ? ORDER BY t_time DESC;",
        session["user_id"],
    )
    return render_template("history.html", transactions=stock_history)