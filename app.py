import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, apology

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = os.getenv("SECRET_KEY") or "b'\xf2F\xff\x9b4\xf1g\xa9\xe7\t\x81&{\xd5\x975\x87\xfb5y>\x0c1\xa1'"

# Configure cs50 to start using site's database
db = SQL("sqlite:///xfiesta.db")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/welcome")
def welcome():
    if not session.get("user_id"):
        return render_template("welcome.html")
    else:
        redirect("/")

@app.route("/login", methods=["POST", "GET"])
def login():
    session.clear()

    if request.method == "GET":
        render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        # Check for existing user and verify
        user_data = db.execute("SELECT id, hash FROM users WHERE username = ?;", username)
        if len(user_data) != 1 or not check_password_hash(user_data[0]["hash"], password):
            return apology("Invalid Username/Password")
        else:
            session["user_id"] = user_data[0]["id"]

        redirect("/")
