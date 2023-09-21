import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify, abort
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, apology

import logging

logging.getLogger("cs50").disabled = False

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


# 404 page
@app.errorhandler(404)
def page_not_found(e):
    return apology("Page Not Found!", 404)


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/welcome")
def welcome():
    if not session.get("user_id"):
        return render_template("welcome.html")
    else:
        return redirect("/")


@app.route("/login", methods=["POST", "GET"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check for existing user and verify
        user_data = db.execute("SELECT id, hash FROM users WHERE username = ?;", username)
        if len(user_data) != 1 or not check_password_hash(user_data[0]["hash"], password):
            return apology("Invalid Username/Password!")
        else:
            session["user_id"] = user_data[0]["id"]
            return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        fullname = request.form.get("name")
        password1 = request.form.get("password")
        password2 = request.form.get("confirm")

        # Verify input
        if not username or not fullname or not password1 or not password2 or password1 != password2 or len(password1) < 8:
            return apology("Invalid Submission!")
        check = db.execute("SELECT * FROM users WHERE username = ?;", username)
        if len(check) > 0:
            return apology("User already exists!")

        # Insert data to db
        db.execute("INSERT INTO users(username, fullname, hash, creation_time) VALUES(?, ?, ?, CURRENT_TIMESTAMP);", username, fullname, generate_password_hash(password1))
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    # Clear session data and redirect to welcome page
    session.clear()
    return redirect("/welcome")


# Check username via AJAX request
@app.route("/check_username", methods=["GET", "POST"])
def check_username():
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        username = request.form.get("username")
        users = db.execute("SELECT * FROM users WHERE username = ?;", username)
        if len(users) > 0:
            return jsonify({"result": False})
        else:
            return jsonify({"result": True})
    else:
        abort(404)


# Profile Page
@app.route("/profile")
@login_required
def profile():
    username = request.args.get("username")

    # User does not exist or is current user
    if (not username or username.strip() == ""):
        user = db.execute("SELECT id, username, fullname, about_me, friends, posts, carnival, creation_time FROM users WHERE id = ?;", session["user_id"])

        interests = db.execute(
                "SELECT interests.interest AS interest FROM interests JOIN user_interests ON user_interests.interest_id = interests.id WHERE user_interests.user_id = ? ORDER BY interests.interest;",
                session["user_id"]
            )
        return render_template("user_profile.html", user=user[0], interests=interests)

    else:
        user = db.execute("SELECT id, username, fullname, about_me, friends, posts, carnival, creation_time FROM users WHERE username = ?;", username)
        if len(user) == 0:
            abort(404)
        elif user[0]["id"] == session["user_id"]:
            return redirect("/profile")

        # Check for friend status
        friends_status = False
        friends = db.execute("SELECT friends FROM friends WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], user[0]["id"])
        if not friends or friends[0]["friends"] == 0:
            friends_status = False
        else:
            friends_status = True

        # Check for interests
        interests = db.execute(
                "SELECT interests.interest AS interest FROM interests JOIN user_interests ON user_interests.interest_id = interests.id WHERE user_interests.user_id = ? ORDER BY interests.interest;",
                user[0]["id"]
            )
        return render_template("o_user_profile.html", user=user[0], interests=interests, friends=friends_status)


# Update friends status via AJAX
@app.route("/manage_friends", methods=["GET", "POST"])
@login_required
def manage_friends():
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        id = request.form.get("user_id")
        try:
            db.execute("BEGIN TRANSACTION")
            friends = db.execute("SELECT friends FROM friends WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], id)
            if not friends:
                db.execute("INSERT INTO friends(user_id1, user_id2, friends) VALUES(?, ?, 1);", session["user_id"], id)
                db.execute("INSERT INTO friends(user_id1, user_id2, friends) VALUES(?, ?, 1);", id, session["user_id"])
                db.execute("UPDATE users SET friends = friends + 1 WHERE id = ? OR id = ?;", session["user_id"], id)
                db.execute("COMMIT")
                return jsonify({"result": True}), 200
            elif friends[0]["friends"] == 0:
                db.execute("UPDATE friends SET friends = 1 WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], id)
                db.execute("UPDATE friends SET friends = 1 WHERE user_id1 = ? AND user_id2 = ?;", id, session["user_id"])
                db.execute("UPDATE users SET friends = friends + 1 WHERE id = ? OR id = ?;", session["user_id"], id)
                db.execute("COMMIT")
                return jsonify({"result": True}), 200
            else:
                db.execute("UPDATE friends SET friends = 0 WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], id)
                db.execute("UPDATE friends SET friends = 0 WHERE user_id1 = ? AND user_id2 = ?;", id, session["user_id"])
                db.execute("DELETE FROM friends WHERE friends = 0;")
                db.execute("UPDATE users SET friends = friends - 1 WHERE id = ? OR id = ?;", session["user_id"], id)
                db.execute("COMMIT")
                return jsonify({"result": False}), 200
        except Exception as e:
            db.execute("ROLLBACK")
            return apology("Friend could not be added/removed!")
    else:
        abort(404)


# Manage Profile Settings
@app.route("/profile_settings", methods=["GET", "POST"])
@login_required
def profile_settings():
    if request.method == "POST":
        ...
    else:
        user = db.execute("SELECT fullname, about_me FROM users WHERE id = ?;", session["user_id"])
        interests = db.execute(
                "SELECT interests.interest AS interest FROM interests JOIN user_interests ON user_interests.interest_id = interests.id WHERE user_interests.user_id = ? ORDER BY interests.interest;",
                session["user_id"]
            )
        return render_template("profile_settings.html", user=user[0], interests=interests)


# User Account Actions
@app.route("/account_settings")
@login_required
def account_settings():
    return render_template("account_settings.html")


# Change User Account Details
@app.route("/change_account", methods=["GET", "POST"])
@login_required
def change_account():
    if request.method == "POST":
        username = request.form.get("username")
        password_old = request.form.get("password_old")
        password_new = request.form.get("password_new")
        password_new2 = request.form.get("password_new2")

        if not username or not password_old or not password_new or not password_new2 or password_new != password_new2:
            return apology("Invalid Submission!")

        check = db.execute("SELECT * FROM users WHERE username = ?;", username)
        if len(check) > 0 and check[0]["id"] != session["user_id"]:
            return apology("Username already exists!")

        user_prev = db.execute("SELECT hash FROM users WHERE id = ?;", session["user_id"])
        if not check_password_hash(user_prev[0]["hash"], password_new):
            return apology("Incorrect Password!")

        db.execute("UPDATE users SET username = ?, hash = ? WHERE id = ?;", username, generate_password_hash(password_new), session["user_id"])

    else:
        user = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])
        return render_template("change_account.html", username=user[0]["username"])


@app.route("/remove_account", methods=["GET", "POST"])
@login_required
def remove_account():
    if request.method == "POST":
        password = request.form.get("password")
        user = db.execute("SELECT hash FROM users WHERE id = ?;", session["user_id"])
        confirm = request.form.get("confirmation")
        if not confirm or not check_password_hash(user[0]["hash"], password):
            return apology("Invalid Submission Or Incorrect Password!")
        elif confirm == "No":
            return redirect("/account_settings")
        elif confirm == "Yes" and check_password_hash(user[0]["hash"], password):
            try:
                db.execute("BEGIN TRANSACTION")
                db.execute("DELETE FROM users WHERE id = ?;", session["user_id"])
                db.execute("DELETE FROM user_interests WHERE user_id = ?;", session["user_id"])
                db.execute("DELETE FROM friends WHERE user_id1 = ? OR user_id2 = ?;", session["user_id"], session["user_id"])
                db.execute("COMMIT")
                session.clear()
                return redirect("/welcome")
            except Exception as e:
                db.execute("ROLLBACK")
                return apology("Account Deletion Failed!")
        else:
            return apology("Invalid Submission!")
    else:
        return render_template("remove_account.html")
