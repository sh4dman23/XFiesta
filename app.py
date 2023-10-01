import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify, abort, send_file
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, apology, check_password
import random
import logging
from markupsafe import Markup, escape


# Logs
logging.getLogger("cs50").disabled = False

log_file = "app.log"
logging.basicConfig(filename=log_file, level=logging.INFO)

# Configure cs50 to start using site's database
db = SQL("sqlite:///xfiesta.db")


list_of_interests = [
    "Gaming",
    "Traveling",
    "Reading",
    "Cooking",
    "Hiking",
    "Photography",
    "Painting",
    "Music",
    "Dancing",
    "Sports",
    "Movies",
    "Writing",
    "Yoga",
    "Meditation",
    "Fishing",
    "Shopping",
    "Swimming",
    "Camping",
    "Skiing",
    "Gardening",
    "Crafts",
    "Singing",
    "Animals",
    "Technology",
    "History",
    "Science",
    "Art",
    "Fashion",
    "Food",
    "Fitness"
]

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = os.getenv("SECRET_KEY") or "b'\xf2F\xff\x9b4\xf1g\xa9\xe7\t\x81&{\xd5\x975\x87\xfb5y>\x0c1\xa1'"


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


# Allow access to server hosted files
@app.route('/server_hosted_files/<path:directory>/<path:filename>')
def get_image(directory, filename):
    # Root directory
    root_dir = './server_hosted_files'

    # Construct path to image
    image_path = os.path.join(root_dir, directory, filename)

    if not os.path.exists(image_path):
        return apology("File Not Found!", 404)

    # Serve image
    return send_file(image_path)


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
    if session.get("user_id"):
        return redirect("/profile")
    if request.method == "POST":
        username = request.form.get("username")
        fullname = request.form.get("name")
        password1 = request.form.get("password")
        password2 = request.form.get("confirm")

        # Verify input
        if not username or not fullname or not password1 or not password2 or password1 != password2 or len(fullname) > 70 or not check_password(password1):
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


# Check username
@app.route("/api/check_username", methods=["POST"])
def check_username():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)
    username = request.form.get("username")
    users = db.execute("SELECT * FROM users WHERE username = ?;", username)
    # Username already exists
    if len(users) > 0:
        return jsonify({"result": False})
    # Username is free to use
    else:
        return jsonify({"result": True})


# Check password
@app.route("/api/check_password", methods=["POST"])
def check_password_api():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)

    data = request.get_json()

    if not data or not data.get("password"):
        return jsonify({"result": False}), 400

    # Check1 is used in login, change_account and delete_account (remove_account) for checking user's current password
    if session.get("user_id"):
        info = db.execute("SELECT hash FROM users WHERE id = ?;", session["user_id"])
        check1 = check_password_hash(info[0]["hash"], data["password"])
    else:
        check1 = False

    user_exists = False

    if data.get("username"):
        user = db.execute("SELECT hash FROM users WHERE username = ?;", data["username"])
        if not user:
            user_exists = False
            check1 = False
        else:
            user_exists = True
            check1 = check_password_hash(user[0]["hash"], data["password"])


    # Check2 is used in register and change_account to check if whether or not the new password has enough of each type of characters
    check2 = check_password(data["password"])

    response = {
        "result": True,
        "check1": check1,
        "check2": check2,
        "user_exists": user_exists
    }
    return jsonify(response), 200


# Home page
@app.route("/")
@login_required
def index():
    user = db.execute("SELECT id, username, fullname, pfp_location FROM users WHERE id = ?;", session["user_id"])
    notifications = db.execute("SELECT id, href, details, status FROM notifications WHERE user_id = ? AND status = 'unread' ORDER BY n_time DESC;", session["user_id"])
    notification_count = len(notifications) if notifications else 0
    return render_template("home.html", user=user[0], notifications=notifications, notification_count=notification_count)


# Marks notifications as read
@app.route("/api/mark_notification_as_read", methods=["POST"])
@login_required
def mark_as_read():
    if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
        abort(404)

    data = request.get_json()
    if not data or not (data.get("id") or data.get("optional")):
        return jsonify({"result": False}), 400

    # Mark all as read
    try:
        if data.get("optional") and data["optional"] == "all":
            db.execute("UPDATE notifications SET status = 'read' WHERE user_id = ?;", session["user_id"])
        elif data.get("id"):
            db.execute("UPDATE notifications SET status = 'read' WHERE id = ?;", data["id"])
        return jsonify({"result": True}), 200
    except Exception as e:
        return jsonify({"result": False}), 400


# Profile Page
@app.route("/profile", defaults={"username": ""})
@app.route("/profile/", defaults={"username": ""})
@app.route("/profile/<username>")
@login_required
def profile(username):

    # No username
    if (not username or username == ""):
        user = db.execute("SELECT id, username, fullname, about_me, pfp_location, friends, posts, carnival, creation_time FROM users WHERE id = ?;", session["user_id"])

        interests = db.execute(
                "SELECT interests.interest AS interest FROM interests JOIN user_interests ON user_interests.interest_id = interests.id WHERE user_interests.user_id = ? ORDER BY interests.interest;",
                session["user_id"]
            )
        return render_template("user_profile.html", user=user[0], interests=interests)

    else:
        user = db.execute("SELECT id, username, fullname, about_me, pfp_location, friends, posts, carnival, creation_time FROM users WHERE username = ?;", username)
        if not user:
            abort(404)
        elif user[0]["id"] == session["user_id"]:
            return redirect("/profile")

        # Check for friend status
        friends = db.execute("SELECT friends FROM friends WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], user[0]["id"])
        if not friends:
            status = 0
        else:
            if friends[0]["friends"] not in [0, 1, 2, 3]:
                abort(404)
            else:
                status = friends[0]["friends"]
        # Check for interests
        interests = db.execute(
                "SELECT interests.interest AS interest FROM interests JOIN user_interests ON user_interests.interest_id = interests.id WHERE user_interests.user_id = ? ORDER BY interests.interest;",
                user[0]["id"]
            )
        return render_template("o_user_profile.html", user=user[0], interests=interests, friends_status=status)


# Update friends status via AJAX (Only handles friend requests, request declination and friend removal). DOES NOT HANDLE ACCEPT REQUESTS!
@app.route("/api/manage_friends", methods=["POST"])
@login_required
def manage_friends():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)

    id = request.form.get("user_id")

    if not id or not id.isdigit() or id == session["user_id"]:
        return jsonify({"result": "Failed"})

    id = int(id)

    user = db.execute("SELECT username FROM users WHERE id = ?;", id)
    self = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])

    if not user:
        return jsonify({"result": "Failed"})
    try:
        db.execute("BEGIN TRANSACTION;")
        friends = db.execute("SELECT friends FROM friends WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], id)
        if not friends:
            db.execute("INSERT INTO friends(user_id1, user_id2, friends) VALUES(?, ?, 2);", session["user_id"], id)
            db.execute("INSERT INTO friends(user_id1, user_id2, friends) VALUES(?, ?, 3);", id, session["user_id"])

            # Send notification to user
            details = "@" + self[0]["username"] + " sent you a friend request."
            db.execute("INSERT INTO notifications(user_id, href, details) VALUES (?, ?, ?);", id, "/profile/" + self[0]["username"], details)

            db.execute("COMMIT;")
            return jsonify({"result": "Request Sent"}), 200
        elif friends[0]["friends"] == 0:
            db.execute("UPDATE friends SET friends = 2 WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], id)
            db.execute("UPDATE friends SET friends = 3 WHERE user_id1 = ? AND user_id2 = ?;", id, session["user_id"])

            # Send notification to user
            details = "@" + self[0]["username"] + " sent you a friend request."
            db.execute("INSERT INTO notifications(user_id, href, details) VALUES (?, ?, ?);", id, "/profile/" + self[0]["username"], details)

            db.execute("COMMIT;")
            return jsonify({"result": "Request Sent"}), 200
        else:
            db.execute("UPDATE friends SET friends = 0 WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], id)
            db.execute("UPDATE friends SET friends = 0 WHERE user_id1 = ? AND user_id2 = ?;", id, session["user_id"])

            if friends[0]["friends"] == 2:
                # Remove send request notification
                details = "@" + self[0]["username"] + " sent you a friend request."
                db.execute("DELETE FROM notifications WHERE user_id = ? AND details = ?;", id, details)

            elif friends[0]["friends"] == 3:
                # Remove send request notification (saved in user's own notifications)
                details = "@" + user[0]["username"] + " sent you a friend request."
                db.execute("DELETE FROM notifications WHERE user_id = ? AND details = ?;", session["user_id"], details)

            db.execute("DELETE FROM friends WHERE friends = 0;")

            if friends[0]["friends"] == 1:
                db.execute("UPDATE users SET friends = friends - 1 WHERE id = ? OR id = ?;", session["user_id"], id)

            db.execute("COMMIT;")
            return jsonify({"result": "Removed Friend"}), 200
    except Exception as e:
        db.execute("ROLLBACK;")
        return jsonify({"result": "Failed"}), 400


# Handles Accept Requests
@app.route("/api/accept_friend_request", methods=["POST"])
def accept_friend_request():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)

    friend_id = request.form.get("user_id")
    if not friend_id or friend_id == session["user_id"]:
        return jsonify({"result": False}), 400

    friend_id = int(friend_id)

    user = db.execute("SELECT username FROM users WHERE id = ?;", friend_id)
    self = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])

    try:
        db.execute("BEGIN TRANSACTION;")

        # Check for validity of request
        status = db.execute("SELECT friends FROM friends WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], friend_id)
        if not status or status[0]["friends"] != 3:
            db.execute("ROLLBACK;")
            return jsonify({"result": False}), 400

        db.execute(
            "UPDATE friends SET friends = 1 WHERE (user_id1 = ? AND user_id2 = ?) OR (user_id1 = ? AND user_id2 = ?);"
            , session["user_id"], friend_id, friend_id, session["user_id"]
        )
        db.execute("UPDATE users SET friends = friends + 1 WHERE id = ? OR id = ?;", session["user_id"], friend_id)

        # Delete notification to user about friend request
        details = "@" + user[0]["username"] + " sent you a friend request."
        db.execute("DELETE FROM notifications WHERE user_id = ? AND details = ?;", session["user_id"], details)

        # Send notification to friend about acceptance
        details = "@" + self[0]["username"] + " accepted your friend request."
        db.execute("INSERT INTO notifications(user_id, href, details) VALUES (?, ?, ?);", friend_id, "/profile/" + self[0]["username"], details)

        db.execute("COMMIT;")
        return jsonify({"result": True}), 200

    except Exception as e:
        db.execute("ROLLBACK;")
        return jsonify({"result": False}), 400


# Manage Profile Settings
@app.route("/profile_settings", methods=["GET", "POST"])
@login_required
def profile_settings():
    if request.method == "POST":
        pfp = request.files["profile_pic"]
        fullname = request.form.get("name")
        about_me = request.form.get("about_me")
        interest_list = request.form.getlist("interest")

        if pfp and pfp != "":
                # Sanitize and validate input
                pfp.filename = secure_filename(pfp.filename).lower()
                if not pfp.filename.endswith(".png") and not pfp.filename.endswith(".jfif") and not pfp.filename.endswith(".pjp") and not pfp.filename.endswith(".jpg") and not pfp.filename.endswith(".jpeg") and not pfp.filename.endswith(".pjpeg"):
                    raise Exception("Invalid Image Format!")

        if not fullname or len(fullname) > 70 or len(about_me) > 640:
            return apology("Invalid Submission!")

        try:
            db.execute("BEGIN TRANSACTION;")
            prev_pfp = db.execute("SELECT pfp_location FROM users WHERE id = ?;", session["user_id"])
            # If the user had a pfp before
            if prev_pfp[0]["pfp_location"]:
                # First delete previous pfp (if it is not the default one)
                if os.path.exists(prev_pfp[0]["pfp_location"]) and prev_pfp[0]["pfp_location"] != "server_hosted_files/profile_pics/default_profile_pic/user_profile_pic.png":
                    try:
                        os.remove(prev_pfp[0]["pfp_location"])
                    except OSError:
                        pass

                # Update if new
                if pfp:
                    dir = os.path.dirname(prev_pfp[0]["pfp_location"])
                    if dir == os.path.join("server_hosted_files", "profile_pics", "default_profile_pic"):
                        dir = os.path.join("server_hosted_files", "profile_pics", str(session["user_id"]))
                        if not os.path.exists(dir):
                            try:
                                os.makedirs(dir)
                            except OSError:
                                raise Exception("Could not make directory for pfp!")

                    pfp_location = os.path.join(dir, str(pfp.filename))
                    pfp.save(pfp_location)
                # Reset to default
                else:
                    pfp_location = "server_hosted_files/profile_pics/default_profile_pic/user_profile_pic.png"
            else:
                # If uploaded, save else no change
                if pfp:
                    pfp_location = os.path.join("server_hosted_files", "profile_pics", str(session["user_id"]))
                    if not os.path.exists(pfp_location):
                        try:
                            os.makedirs(pfp_location)
                        except OSError:
                            raise Exception("Could not make directory for pfp!")
                    pfp_location = os.path.join(pfp_location, str(pfp.filename))
                    pfp.save(pfp_location)
                else:
                    pfp_location = "server_hosted_files/profile_pics/default_profile_pic/user_profile_pic.png"


            db.execute("UPDATE users SET fullname = ?, about_me = ?, pfp_location = ? WHERE id = ?;", fullname, about_me, pfp_location, session["user_id"])
            db.execute("DELETE FROM user_interests WHERE user_id = ?;", session["user_id"])

            if interest_list:
                for interest in interest_list:
                    if interest in list_of_interests:
                        interest_id = db.execute("SELECT id FROM interests WHERE interest = ?;", interest)
                        db.execute("INSERT INTO user_interests(user_id, interest_id) VALUES(?, ?);", session["user_id"], interest_id[0]["id"])
                    else:
                        raise Exception("Invalid tags")

            db.execute("COMMIT;")
        except Exception as e:
            db.execute("ROLLBACK;")
            logging.error(e)
            return apology("Invalid Submission!")

        return redirect("/profile")
    else:
        user = db.execute("SELECT fullname, about_me, pfp_location FROM users WHERE id = ?;", session["user_id"])
        interests = db.execute(
            "SELECT interests.interest AS interest FROM interests JOIN user_interests ON user_interests.interest_id = interests.id WHERE user_interests.user_id = ? ORDER BY interests.interest;",
            session["user_id"]
        )
        if interests:
            return render_template("profile_settings.html", user=user[0], user_interests=interests, list_of_interests=list_of_interests)
        else:
            return render_template("profile_settings.html", user=user[0], list_of_interests=list_of_interests)


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

        if not username or not password_old or not password_new or not password_new2 or password_new != password_new2 or not check_password(password_new):
            return apology("Invalid Submission!")

        check = db.execute("SELECT id FROM users WHERE username = ?;", username)
        if len(check) > 0 and check[0]["id"] != session["user_id"]:
            return apology("Username already exists!")

        user_prev = db.execute("SELECT hash FROM users WHERE id = ?;", session["user_id"])
        if not check_password_hash(user_prev[0]["hash"], password_old):
            return apology("Incorrect Password!")

        db.execute("UPDATE users SET username = ?, hash = ? WHERE id = ?;", username, generate_password_hash(password_new), session["user_id"])
        return redirect("/profile")
    else:
        user = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])
        return render_template("change_account.html", username=user[0]["username"])


# Friends Page
@app.route("/friends")
@login_required
def friends():
    friends = db.execute("SELECT DISTINCT id, username, fullname, pfp_location FROM users WHERE id IN (SELECT user_id2 FROM friends WHERE user_id1 = ? AND friends = 1);", session["user_id"])
    requests = db.execute("SELECT DISTINCT id, username, fullname, pfp_location FROM users WHERE id IN (SELECT user_id2 FROM friends WHERE user_id1 = ? AND friends = 3);", session["user_id"])
    recommendations = db.execute(
        """
        SELECT DISTINCT u.id AS id, u.username AS username, u.fullname AS fullname, u.pfp_location AS pfp_location
        FROM users AS u
        JOIN user_interests ui ON u.id = ui.user_id
        WHERE ui.interest_id IN (SELECT interest_id FROM user_interests WHERE user_id = ?)
        AND u.id != ?
        AND u.id NOT IN (SELECT user_id2 FROM friends WHERE user_id1 = ? AND friends != 0)
        LIMIT 20;
        """
        , session["user_id"], session["user_id"], session["user_id"]
    )

    random.shuffle(recommendations)
    return render_template("friends.html", friends=friends, requests=requests, recommendations=recommendations)


@app.route("/post", defaults={"post_id": ""})
@app.route("/post/", defaults={"post_id": ""})
@app.route("/post/<post_id>")
@login_required
def post(post_id):
    post = db.execute("SELECT *, strftime('%d-%m-%Y', post_time) AS date, strftime('%H:%M', post_time) AS time FROM posts WHERE id = ?;", post_id)
    if not post_id or not post:
        return redirect("/posts")
    post = post[0]

    # Add tags
    tag_list = list()
    tags = db.execute("SELECT interests.interest AS tag FROM interests JOIN post_tags ON interests.id = post_tags.tag_id WHERE post_tags.post_id = ?;", post_id)
    for tag in tags:
        tag_list.append(tag["tag"])
    post["tags"] = tag_list

    # Check post ownership and get post owner info
    post["owner"] = True if post["user_id"] == session["user_id"] else False
    user = db.execute("SELECT fullname, username, pfp_location FROM users WHERE id = (SELECT user_id FROM posts WHERE id = ?)", post_id)
    post["fullname"] = user[0]["fullname"]
    post["username"] = user[0]["username"]
    post["pfp_location"] = user[0]["pfp_location"]

    # Get post interaction status
    status = db.execute("SELECT status FROM user_post_interactions WHERE user_id = ? AND post_id = ?;", session["user_id"], post_id)
    post["status"] = status[0]["status"] if status else 0

    # Get all comments for post
    comments = db.execute("SELECT *, strftime('%d-%m-%Y', comment_time) AS date, strftime('%H:%M', comment_time) AS time FROM comments WHERE post_id = ? ORDER BY comment_time DESC;", post_id)

    if comments:
        for comment in comments:
            comment["owner"] = True if comment["user_id"] == session["user_id"] else False

            user = db.execute("SELECT fullname, username, pfp_location FROM users WHERE id = ?;", comment["user_id"])
            comment["fullname"] = user[0]["fullname"]
            comment["username"] = user[0]["username"]
            comment["pfp_location"] = user[0]["pfp_location"]

            status = db.execute("SELECT status FROM user_comment_interactions WHERE comment_id = ? AND user_id = ?;", comment["id"], session["user_id"])
            comment["status"] = status[0]["status"] if status else 0


    return render_template("post_page.html", post=post, comments=comments)


@app.route("/posts")
@login_required
def posts():
    # Get user's posts
    my_posts = db.execute("SELECT *, strftime('%d-%m-%Y', post_time) AS date, strftime('%H:%M', post_time) AS time FROM posts WHERE user_id = ? ORDER BY post_time DESC;", session["user_id"])
    for post in my_posts:
        tag_list = list()
        tags = db.execute("SELECT interests.interest AS tag FROM interests JOIN post_tags ON post_tags.tag_id = interests.id WHERE post_id = ? ORDER BY tag;", post["id"])
        for tag in tags:
            tag_list.append(tag["tag"])
        post["tags"] = tag_list

        # Set user_post_interaction status - 0 for no interaction, 1 for liked, 2 for disliked
        interaction_status = db.execute("SELECT status FROM user_post_interactions WHERE post_id = ? AND user_id = ?;", post["id"], session["user_id"])
        post["status"] = 0 if not interaction_status else interaction_status[0]["status"]

    user = db.execute("SELECT fullname, username, pfp_location FROM users WHERE id = ?;", session["user_id"])

    # Get user's friends' posts
    friend_posts = db.execute("SELECT *, strftime('%d-%m-%Y', post_time) AS date, strftime('%H:%M', post_time) AS time FROM posts WHERE user_id IN (SELECT user_id2 FROM friends WHERE user_id1 = ?) ORDER BY post_time DESC;", session["user_id"])
    for post in friend_posts:
        info = db.execute("SELECT fullname, username, pfp_location FROM users WHERE id = ?;", post["user_id"])
        post["fullname"] = info[0]["fullname"]
        post["username"] = info[0]["username"]
        post["pfp_location"] = info[0]["pfp_location"]

        tag_list2 = list()
        tags = db.execute("SELECT interests.interest AS tag FROM interests JOIN post_tags ON post_tags.tag_id = interests.id WHERE post_id = ? ORDER BY tag;", post["id"])
        for tag in tags:
            tag_list2.append(tag["tag"])
        post["tags"] = tag_list2

        # Set user_post_interaction status - 0 for no interaction, 1 for liked, 2 for disliked
        interaction_status = db.execute("SELECT status FROM user_post_interactions WHERE post_id = ? AND user_id = ?;", post["id"], session["user_id"])
        post["status"] = 0 if not interaction_status else interaction_status[0]["status"]

    return render_template("posts.html", my_posts=my_posts, my_name=user[0]["fullname"], my_username=user[0]["username"], my_pfp = user[0]["pfp_location"], friend_posts=friend_posts)


# Allows users to create posts
@app.route("/createpost", methods=["GET", "POST"])
@login_required
def createpost():
    if request.method == "POST":
        image = request.files["image-upload"]
        title = request.form.get("title")
        contents = request.form.get("contents")
        tags = request.form.getlist("tag")


        # Validate input
        if not title or not contents or not tags or len(title) > 70 or len(contents) > 640:
            return apology("Invalid Submission!")

        try:
            db.execute("BEGIN TRANSACTION;")

            # Add post to database
            post_id = db.execute("INSERT INTO posts(user_id, title, contents, likes, post_time) VALUES(?, ?, ?, 1, CURRENT_TIMESTAMP);" , session["user_id"], title, contents)
            db.execute("INSERT INTO user_post_interactions(post_id, user_id, status, timestamp) VALUES(?, ?, 1, CURRENT_TIMESTAMP);", post_id, session["user_id"])
            # Increase post count for user
            db.execute("UPDATE users SET posts = posts + 1, carnival = carnival + 2 WHERE id = ?;", session["user_id"])

            # If image was uploaded
            if image and image != "":

                # Sanitize and validate input
                image.filename = secure_filename(image.filename).lower()
                if not image.filename.endswith(".png") and not image.filename.endswith(".jfif") and not image.filename.endswith(".pjp") and not image.filename.endswith(".jpg") and not image.filename.endswith(".jpeg") and not image.filename.endswith(".pjpeg"):
                    raise Exception("Invalid Image Format!")

                # Save image in server
                imagelocation = os.path.join("server_hosted_files", "posts", str(post_id))
                if not os.path.exists(imagelocation):
                    os.makedirs(imagelocation)
                imagelocation = os.path.join(imagelocation, str(image.filename))
                image.save(imagelocation)
                db.execute("UPDATE posts SET imagelocation = ? WHERE id = ?;", str(imagelocation), post_id)

            # Add post tags
            for tag in tags:
                if tag in list_of_interests:
                    tag_id = db.execute("SELECT id FROM interests WHERE interest = ?;", tag)
                    db.execute("INSERT INTO post_tags(post_id, tag_id) VALUES(?, ?);", post_id, tag_id[0]["id"])
                else:
                    raise Exception("Invalid Tags!")

            # Everything completed successfully
            db.execute("COMMIT;")
        except Exception as e:
            db.execute("ROLLBACK;")
            return apology(f"{e}")

        return redirect("/posts")
    else:
        return render_template("create_a_post.html", list_of_tags=list_of_interests)


# Edit posts
@app.route("/edit_post", defaults={"post_id": ""}, methods=["GET", "POST"])
@app.route("/edit_post/", defaults={"post_id": ""}, methods=["GET", "POST"])
@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if request.method == "POST":
        post_id = request.form.get("post_id")
        title = request.form.get("title")
        contents = request.form.get("contents")
        tags = request.form.getlist("tag")
        image = request.files["image-upload"]
        change = request.form.get("change")

        if not post_id or not post_id.isdigit or not title or not contents or len(title) > 70 or len(contents) > 640 or not tags or change not in ["unchanged", "changed"]:
            return apology("Invalid Submission!")

        # If an image has been uploaded
        if image and image != "":
            image.filename = secure_filename(image.filename)

            # Validate
            if not image.filename.endswith(".png") and not image.filename.endswith(".jfif") and not image.filename.endswith(".pjp") and not image.filename.endswith(".jpg") and not image.filename.endswith(".jpeg") and not image.filename.endswith(".pjpeg"):
                return apology("Invalid Image Format!")

            image_uploaded = True
        else:
            image_uploaded = False

        # Check if user is the owner of post
        check = db.execute("SELECT user_id FROM posts WHERE id = ?;", post_id)
        if len(check) != 1:
            return apology("Post Not Found!", 404)
        if check[0]["user_id"] != session["user_id"]:
            return apology("Unauthorized Access!", 401)

        prev_image = db.execute("SELECT imagelocation FROM posts WHERE id = ?;", post_id)

        # If previously a server hosted image existed
        if prev_image[0]["imagelocation"]:
            if change == "changed":
                prev_img_dir = os.path.dirname(prev_image[0]["imagelocation"])

                # Delete previous image (if found on server)
                try:
                    os.remove(prev_image[0]["imagelocation"])
                except OSError:
                    pass

                if image_uploaded:
                    # Add new image to previous directory
                    save_location = os.path.join(prev_img_dir, image.filename)
                    image.save(save_location)
                    imagelocation = str(save_location)
                else:
                    # Remove image directory (if found)
                    if os.path.exists(prev_img_dir) and not os.listdir(prev_img_dir):
                        try:
                            os.removedirs(prev_img_dir)
                        except OSError:
                            pass
                    imagelocation = None

            # Don't need to do anything if status is unchanged

        else:
            if image_uploaded:
                # Create new directory to save image
                new_dir = os.path.join("server_hosted_files", "posts", post_id)

                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                save_location = os.path.join(new_dir, str(image.filename))
                image.save(save_location)
                imagelocation = save_location
            else:
                imagelocation = None

        # Update database
        try:
            db.execute("BEGIN TRANSACTION;")
            db.execute("UPDATE posts SET title = ?, contents = ? WHERE id = ?;", title, contents, post_id)

            # Update tags
            db.execute("DELETE FROM post_tags WHERE post_id = ?;", post_id)
            for tag in tags:
                if tag in list_of_interests:
                    tagId = db.execute("SELECT id FROM interests WHERE interest = ?;", tag)
                    db.execute("INSERT INTO post_tags(tag_id, post_id) VALUES (?, ?);", tagId[0]["id"], post_id)

            # Update image
            if image_uploaded:
                db.execute("UPDATE posts SET imagelocation = ? WHERE id = ?;", imagelocation, post_id)
            elif change == "changed" and prev_image[0]["imagelocation"]:
                db.execute("UPDATE posts SET imagelocation = NULL WHERE id = ?;", post_id)

            db.execute("COMMIT;")

        except Exception as e:
            db.execute("ROLLBACK;")
            logging.error(f"An error occured: {e}")
            return apology(f"Your request could not be handled! - {e}")

        return redirect("/posts")

    else:
        # If not found, redirect to posts
        if not post_id or post_id == "":
            return redirect("/posts")

        post = db.execute("SELECT * FROM posts WHERE id = ?;", post_id)
        tags = db.execute("SELECT interests.interest AS tag FROM interests JOIN post_tags ON post_tags.tag_id = interests.id WHERE post_id = ? ORDER BY tag;", post_id)
        if not post or not tags or post[0]["user_id"] != session["user_id"]:
            print("b")
            return redirect("/posts")

        tag_list = list()
        for tag in tags:
            tag_list.append(tag["tag"])

        post[0]["tags"] = tag_list

        return render_template("edit_post.html", post=post[0], list_of_tags=list_of_interests)


# Manage post likes/dislikes
@app.route("/api/manage_likes", methods=["POST"])
@login_required
def manage_likes():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)

    post_id = request.form.get("post_id")
    action = request.form.get("action")

    # Verify
    if not post_id or post_id == "" or not action or action not in ["like", "dislike"]:
        return jsonify({"result": False}), 400

    # Update
    try:
        db.execute("BEGIN TRANSACTION;")
        status = db.execute("SELECT status FROM user_post_interactions WHERE post_id = ? AND user_id = ?;", post_id, session["user_id"])

        # AJAX request from like manager
        if action == "like":
            if status:
                # Like post
                if status[0]["status"] == 0:
                    db.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?;", post_id)
                    db.execute("UPDATE user_post_interactions SET status = 1, timestamp = CURRENT_TIMESTAMP WHERE post_id = ? AND user_id = ?;", post_id, session["user_id"])
                    db.execute("UPDATE users SET carnival = carnival + 2 WHERE id = (SELECT user_id FROM posts WHERE id = ?);", post_id)

                # Remove like status (unlike)
                elif status[0]["status"] == 1:
                    db.execute("UPDATE posts SET likes = likes - 1 WHERE id = ?;", post_id)
                    db.execute("UPDATE user_post_interactions SET status = 0, timestamp = CURRENT_TIMESTAMP WHERE post_id = ? AND user_id = ?;", post_id, session["user_id"])
                    db.execute("UPDATE users SET carnival = carnival - 2 WHERE id = (SELECT user_id FROM posts WHERE id = ?);", post_id)

                # Disliked previously, now wants to like => Remove dislike(+1) and then like(+1)
                elif status[0]["status"] == 2:
                    db.execute("UPDATE posts SET likes = likes + 2 WHERE id = ?;", post_id)
                    db.execute("UPDATE user_post_interactions SET status = 1, timestamp = CURRENT_TIMESTAMP WHERE post_id = ? AND user_id = ?;", post_id, session["user_id"])
                    db.execute("UPDATE users SET carnival = carnival + 4 WHERE id = (SELECT user_id FROM posts WHERE id = ?);", post_id)

            # Status is considered 0 (no interaction) and hence, like post
            else:
                db.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?;", post_id)
                db.execute("INSERT INTO user_post_interactions(status, post_id, user_id, timestamp) VALUES(1, ?, ?, CURRENT_TIMESTAMP);", post_id, session["user_id"])
                db.execute("UPDATE users SET carnival = carnival + 2 WHERE id = (SELECT user_id FROM posts WHERE id = ?);", post_id)

        # AJAX request from dislike manager
        else:
            if status:
                # Dislike post
                if status[0]["status"] == 0:
                    db.execute("UPDATE posts SET likes = likes - 1 WHERE id = ?;", post_id)
                    db.execute("UPDATE user_post_interactions SET status = 2, timestamp = CURRENT_TIMESTAMP WHERE post_id = ? AND user_id = ?;", post_id, session["user_id"])
                    db.execute("UPDATE users SET carnival = carnival - 2 WHERE id = (SELECT user_id FROM posts WHERE id = ?);", post_id)

                # Remove dislike status
                elif status[0]["status"] == 2:
                    db.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?;", post_id)
                    db.execute("UPDATE user_post_interactions SET status = 0, timestamp = CURRENT_TIMESTAMP WHERE post_id = ? AND user_id = ?;", post_id, session["user_id"])
                    db.execute("UPDATE users SET carnival = carnival + 2 WHERE id = (SELECT user_id FROM posts WHERE id = ?);", post_id)

                # Liked previously, now wants to dislike => Remove like(-1) and then dislike(-1)
                elif status[0]["status"] == 1:
                    db.execute("UPDATE posts SET likes = likes - 2 WHERE id = ?;", post_id)
                    db.execute("UPDATE user_post_interactions SET status = 2 WHERE post_id = ? AND user_id = ?;", post_id, session["user_id"])
                    db.execute("UPDATE users SET carnival = carnival - 4 WHERE id = (SELECT user_id FROM posts WHERE id = ?);", post_id)

            # Status is considered 0 (no interaction) and hence, dislike post
            else:
                db.execute("UPDATE posts SET likes = likes - 1 WHERE id = ?;", post_id)
                db.execute("INSERT INTO user_post_interactions(status, post_id, user_id, timestamp) VALUES(2, ?, ?, CURRENT_TIMESTAMP);", post_id, session["user_id"])
                db.execute("UPDATE users SET carnival = carnival - 2 WHERE id = (SELECT user_id FROM posts WHERE id = ?);", post_id)

        db.execute("COMMIT;")
        return jsonify({"result": True}), 200

    except Exception as e:
        db.execute("ROLLBACK;")
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"result": False}), 400


# Delete posts (via AJAX)
@app.route("/api/delete_post", methods=["POST"])
@login_required
def delete_post():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)

    post_id = request.form.get("post_id")
    if not post_id or post_id == "":
        return jsonify({"result": False})
    user_id = db.execute("SELECT user_id FROM posts WHERE id = ?;", post_id)

    if user_id[0]["user_id"] != session["user_id"]:
        return jsonify({"result": False})

    try:
        db.execute("BEGIN TRANSACTION;")

        # Decrease post count and remove points gained by user's own like. Interactions by others remain unchanged
        comment_count = db.execute("SELECT COUNT(id) AS count FROM comments WHERE post_id = ?;", post_id)
        db.execute("UPDATE users SET posts = posts - 1, carnival = carnival - (2 + ?) WHERE id = ?;", comment_count[0]["count"], session["user_id"])

        # Delete tags
        db.execute("DELETE FROM post_tags WHERE post_id = ?;", post_id)

        # Delete user-post interaction status
        db.execute("DELETE FROM user_post_interactions WHERE post_id = ?;", post_id)

        # Delete all user-comment interactions and comments
        db.execute("DELETE FROM user_comment_interactions WHERE comment_id IN (SELECT id FROM comments WHERE post_id = ?);", post_id)
        db.execute("DELETE FROM comments WHERE post_id = ?;", post_id)

        # Delete server hosted file
        image = db.execute("SELECT imagelocation FROM posts WHERE id = ?;", post_id)
        if image[0]["imagelocation"]:
            try:
                # Remove image
                os.remove(image[0]["imagelocation"])
                directory = os.path.dirname(image[0]["imagelocation"])

                # Remove folder (if empty)
                if os.path.exists(directory) and not os.listdir(directory):
                    os.removedirs(directory)
            except OSError:
                pass

        # Delete post data
        db.execute("DELETE FROM posts WHERE id = ?;", post_id)
        db.execute("COMMIT;")
        return jsonify({"result": True})
    except Exception as e:
        db.execute("ROLLBACK;")
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"result": False})


# Manage comment submissions
@app.route("/api/add_comment", methods=["POST"])
@login_required
def add_comment():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)
    data = request.get_json()
    print(data)

    if not data or not data.get("post_id") or not data.get("comment_contents") or len(data["comment_contents"]) > 640:
        return jsonify({"result": False}), 400
    try:
        db.execute("BEGIN TRANSACTION;")
        comment_id = db.execute("INSERT INTO comments(post_id, user_id, contents, likes) VALUES(?, ?, ?, 1);", data["post_id"], session["user_id"], data["comment_contents"])
        db.execute("INSERT INTO user_comment_interactions(comment_id, user_id, status) VALUES(?, ?, 1);", comment_id, session["user_id"])
        info = db.execute("SELECT strftime('%d-%m-%Y', comment_time) AS date, strftime('%H:%M', comment_time) AS time FROM comments WHERE id = ?;", comment_id)
        db.execute("UPDATE posts SET comments = comments + 1 WHERE id = ?;", data["post_id"])
        db.execute("UPDATE users SET carnival = carnival + 1 WHERE id = ?;", session["user_id"])
        db.execute("COMMIT;")
    except Exception as e:
        db.execute("ROLLBACK")
        logging.error(f"Error: {e}")
        return jsonify({"result": False}), 400

    user = db.execute("SELECT fullname, username, pfp_location FROM users WHERE id = ?;", session["user_id"])

    # Give back sanitized comment
    comment = db.execute("SELECT contents FROM comments WHERE id = ?;", comment_id)
    response = {
        "result": True,
        "comment_id": comment_id,
        "comment_contents": escape(comment[0]["contents"]),
        "fullname": user[0]["fullname"],
        "username": user[0]["username"],
        "pfp_location": user[0]["pfp_location"],
        "date": info[0]["date"],
        "time": info[0]["time"],
    }
    return jsonify(response)


# Manage comment likes/dislikes
@app.route("/api/manage_comment_likes", methods=["POST"])
@login_required
def manage_comment_likes():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)
    data = request.get_json()
    if not data or data["action"] not in ["like", "dislike"]:
        return jsonify({"result": False})
    try:
        db.execute("BEGIN TRANSACTION;")

        # Get interaction status
        status = db.execute("SELECT status FROM user_comment_interactions WHERE comment_id = ? AND user_id = ?;", data["comment_id"], session["user_id"])

        if data["action"] == "like":
            # Add like(+1)
            if not status or status[0]["status"] == 0:
                db.execute("UPDATE comments SET likes = likes + 1 WHERE id = ?;", data["comment_id"])
                db.execute("UPDATE users SET carnival = carnival + 1 WHERE id = (SELECT user_id FROM comments WHERE id = ?);", data["comment_id"])

                if not status:
                    db.execute("INSERT INTO user_comment_interactions(user_id, comment_id, status) VALUES(?, ?, 1);", session["user_id"], data["comment_id"])
                else:
                    db.execute("UPDATE user_comment_interactions SET status = 1 WHERE comment_id = ? AND user_id = ?;", data["comment_id"], session["user_id"])
            # Remove like(-1)
            elif status[0]["status"] == 1:
                db.execute("UPDATE comments SET likes = likes - 1 WHERE id = ?;", data["comment_id"])
                db.execute("UPDATE users SET carnival = carnival - 1 WHERE id = (SELECT user_id FROM comments WHERE id = ?);", data["comment_id"])
                db.execute("UPDATE user_comment_interactions SET status = 0 WHERE comment_id = ? AND user_id = ?;", data["comment_id"], session["user_id"])
            # Remove dislike(+1) and then add like(+1) => +2
            else:
                db.execute("UPDATE comments SET likes = likes + 2 WHERE id = ?;", data["comment_id"])
                db.execute("UPDATE users SET carnival = carnival + 2 WHERE id = (SELECT user_id FROM comments WHERE id = ?);", data["comment_id"])
                db.execute("UPDATE user_comment_interactions SET status = 1 WHERE comment_id = ? AND user_id = ?;", data["comment_id"], session["user_id"])
        else:
            # Add dislike
            if not status or status[0]["status"] == 0:
                db.execute("UPDATE comments SET likes = likes - 1 WHERE id = ?;", data["comment_id"])
                db.execute("UPDATE users SET carnival = carnival - 1 WHERE id = (SELECT user_id FROM comments WHERE id = ?);", data["comment_id"])
                if not status:
                    db.execute("INSERT INTO user_comment_interactions(user_id, comment_id, status) VALUES(?, ?, 2);", session["user_id"], data["comment_id"])
                else:
                    db.execute("UPDATE user_comment_interactions SET status = 2 WHERE comment_id = ? AND user_id = ?;", data["comment_id"], session["user_id"])
            # Remove dislike(+1)
            elif status[0]["status"] == 2:
                db.execute("UPDATE comments SET likes = likes + 1 WHERE id = ?;", data["comment_id"])
                db.execute("UPDATE users SET carnival = carnival + 1 WHERE id = (SELECT user_id FROM comments WHERE id = ?);", data["comment_id"])
                db.execute("UPDATE user_comment_interactions SET status = 0 WHERE comment_id = ? AND user_id = ?;", data["comment_id"], session["user_id"])
            # Remove like(-1) and then add dislike(-1) => -2
            else:
                db.execute("UPDATE comments SET likes = likes - 2 WHERE id = ?;", data["comment_id"])
                db.execute("UPDATE users SET carnival = carnival - 2 WHERE id = (SELECT user_id FROM comments WHERE id = ?);", data["comment_id"])
                db.execute("UPDATE user_comment_interactions SET status = 2 WHERE comment_id = ? AND user_id = ?;", data["comment_id"], session["user_id"])

        new_status = db.execute("SELECT status FROM user_comment_interactions WHERE comment_id = ? AND user_id = ?;", data["comment_id"], session["user_id"])
        like_count = db.execute("SELECT likes FROM comments WHERE id = ?;", data["comment_id"])
        db.execute("COMMIT;")
    except Exception as e:
        db.execute("ROLLBACK;")
        logging.error(f"Error: {e}")
        print(f"{e}")
        print(data)
        return jsonify({"result": False})

    response = {
            "result": True,
            "comment_status": new_status[0]["status"],
            "comment_like_count": like_count[0]["likes"],
        }
    return jsonify(response)


# Delete comment
@app.route("/api/delete_comment", methods=["POST"])
@login_required
def delete_comment():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)

    comment = request.get_json()
    if not comment:
        return jsonify({"result": False}), 400

    try:
        db.execute("BEGIN TRANSACTION;")
        info = db.execute("SELECT post_id, user_id, likes FROM comments WHERE id = ?;", comment["comment_id"])

        if info[0]["user_id"] != session["user_id"]:
            raise Exception("Unauthorized Access!")

        db.execute("UPDATE posts SET comments = comments - 1 WHERE id = ?;", info[0]["post_id"])

        # Remove points gained by user's own like. Interactions by others remain unchanged
        db.execute("UPDATE users SET carnival = carnival - 1 WHERE id = ?;", info[0]["user_id"])

        db.execute("DELETE FROM user_comment_interactions WHERE comment_id = ?;", comment["comment_id"])
        db.execute("DELETE FROM comments WHERE id = ?;", comment["comment_id"])
        db.execute("COMMIT;")
    except Exception as e:
        db.execute("ROLLBACK;")
        logging.error(f"Error: {e}")
        return jsonify({"result": False}), 400

    return jsonify({"result": True}), 200


# Inbox Page
@app.route("/inbox", defaults={"user_id": ""})
@app.route("/inbox/", defaults={"user_id": ""})
@app.route("/inbox/<user_id>")
@login_required
def inbox(user_id):
    # Default Page
    if not user_id or user_id == '':
        inbox = db.execute(
            """
            SELECT DISTINCT i.id, i.user_id1, i.user_id2, i.messages
            FROM inbox AS i
            JOIN messages AS m
            ON i.id = m.inbox_id
            WHERE i.user_id1 = ? OR i.user_id2 = ?
            ORDER BY (
                SELECT MAX(message_time)
                FROM messages AS m2
                WHERE m2.inbox_id = i.id)
            DESC;
            """,
            session["user_id"], session["user_id"]
        )
        for chat in inbox:
            if chat["user_id1"] == session["user_id"]:
                person_id = chat["user_id2"]
            else:
                person_id = chat["user_id1"]
            person = db.execute("SELECT id, fullname, username, pfp_location FROM users WHERE id = ?;", person_id)
            chat["user_id"] = person[0]["id"]
            chat["fullname"] = person[0]["fullname"]
            chat["username"] = person[0]["username"]
            chat["pfp_location"] = person[0]["pfp_location"]

            message = db.execute("SELECT contents FROM messages WHERE inbox_id = ? ORDER BY message_time DESC LIMIT 1;", chat["id"])
            if message:
                chat["last_message"] = message[0]["contents"][0:56] if len(message[0]["contents"]) >= 56 else message[0]["contents"][0:len(message[0]["contents"])]

        return render_template("inbox.html", inbox = inbox)

    # Messages page
    else:
        # Get user info
        user = db.execute("SELECT id, username, fullname, pfp_location FROM users WHERE id = ?;", user_id)
        inbox = db.execute("SELECT id FROM inbox WHERE (user_id1 = ? AND user_id2 = ?) OR (user_id1 = ? AND user_id2 = ?);", session["user_id"], user_id, user_id, session["user_id"])
        if len(user) != 1:
            return redirect("/inbox")

        if not inbox:
            inbox_id = None
        else:
            inbox_id = inbox[0]["id"]

        # Get messages and shared images
        messages = db.execute(
            """
            SELECT *, strftime('%d-%m', message_time) AS date, strftime('%H:%M', message_time) AS time
            FROM messages
            WHERE inbox_id = ?
            ORDER BY message_time;
            """, inbox_id
        )
        for message in messages:
            message_sender = db.execute("SELECT id, fullname, username FROM users WHERE id = ?;", message["sender_id"])
            message["sender_fullname"] = message_sender[0]["fullname"]
            message["sender_username"] = message_sender[0]["username"]
        return render_template("chat.html",user=user[0], messages=messages, user_id=user_id, inbox_id=inbox_id)


# Send messages to an user
@app.route("/api/send_message", methods=["POST"])
@login_required
def send_message():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)
    data = request.get_json()
    print(data)

    if not data or len(data["contents"]) < 1 or len(data["contents"]) > 640:
        return jsonify({"result": False}), 400

    try:
        db.execute("BEGIN TRANSACTION;")

        # Get sender's (user's) info
        user = db.execute("SELECT fullname, username FROM users WHERE id = ?;", session["user_id"])
        if not user:
            raise Exception("User does not exist!")

        # If inbox doesn't exist yet, check if the other user has initiated it and if not, add it
        if not data.get("inbox_id"):
            inbox = db.execute("SELECT id FROM inbox WHERE (user_id1 = ? AND user_id2 = ?) OR (user_id1 = ? AND user_id2 = ?);", session["user_id"], data["reciever_id"], data["reciever_id"], session["user_id"])
            if inbox:
                inbox_id = inbox[0]["id"]
                db.execute("UPDATE inbox SET messages = messages + 1 WHERE id = ?;", inbox_id)
            else:
                inbox_id = db.execute("INSERT INTO inbox(user_id1, user_id2, messages) VALUES(?, ?, 1);", session["user_id"], data["reciever_id"])
        else:
            inbox_id = data["inbox_id"]
            db.execute("UPDATE inbox SET messages = messages + 1 WHERE id = ?;", inbox_id)

        # Add to messages
        message_id = db.execute("INSERT INTO messages(inbox_id, sender_id, recipient_id, contents) VALUES(?, ?, ?, ?);", inbox_id, session["user_id"], data["reciever_id"], data["contents"])
        message = db.execute("SELECT strftime('%d-%m', message_time) AS date, strftime('%H:%M', message_time) AS time FROM messages WHERE id = ?;", message_id)
        db.execute("COMMIT;")

        response = {
            "result": True,
            "fullname": user[0]["fullname"],
            "username": user[0]["username"],
            "owner": True,
            "inbox_id": inbox_id,
            "message_id": message_id,
            "message_time": message[0]["time"],
            "message_date": message[0]["date"],
            "contents": escape(data["contents"])
        }

        return jsonify(response), 200
    except Exception as e:
        db.execute("ROLLBACK;")
        logging.error(f"Error: {e}")
        return jsonify({"result": False}), 400


# Checks for deleted messages (and sends their IDs if found)
@app.route("/api/check_deleted", methods=["POST"])
@login_required
def check_deleted():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)

    data = request.get_json()

    if not data or not data.get("inbox_id"):
        return jsonify({"result": True, "deleted": False}), 200

    try:
        db.execute("BEGIN TRANSACTION;")

        # Get deleted messages not sent by user
        deleted_messages = db.execute("SELECT message_id FROM deleted_messages WHERE inbox_id = ? AND sender_id != ?;", data["inbox_id"], session["user_id"])

        if not deleted_messages:
            db.execute("COMMIT;")
            return jsonify({"result": True, "deleted": False}), 200

        # Clear deleted messages not sent by user
        db.execute("DELETE FROM deleted_messages WHERE inbox_id = ? AND sender_id != ?;", data["inbox_id"], session["user_id"])
        last_message = db.execute("SELECT id FROM messages WHERE inbox_id = ? ORDER BY id DESC LIMIT 1;", data["inbox_id"])

        response = {
            "result": True,
            "deleted": True,
            "last_message_id": last_message[0]["id"] if last_message else None,
            "deleted_messages": deleted_messages
        }
        db.execute("COMMIT;")
        return jsonify(response)
    except Exception as e:
        db.execute("ROLLBACK;")
        logging.error(e)
        return jsonify({"result": False}), 400


# Checks for new messages (and sends them back if found)
@app.route("/api/check_message", methods=["POST"])
@login_required
def check_message():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)
    data = request.get_json()

    # No message exists yet
    if not data:
        return jsonify({"result": False}), 200

    # If not last_message_id has been sent, it is safe to assume that the inbox is non-existent (yet) or empty
    if not data.get("last_message_id"):
        data["last_message_id"] = 0

    # If inbox id has not been sent check for new one
    if not data.get("inbox_id") or data["inbox_id"] == "":
        inbox = db.execute("SELECT id FROM inbox WHERE (user_id1 = ? AND user_id2 = ?) OR (user_id1 = ? AND user_id2 = ?);", session["user_id"], data["person_id"], data["person_id"], session["user_id"])
        if not inbox:
            return jsonify({"result": True, "new": False, "inbox_id": inbox_id}), 200
        else:
            inbox_id = inbox[0]["id"]
    else:
        inbox_id = data["inbox_id"]

    # Do this when an inbox id has been sent or found (if not sent)
    try:
        db.execute("BEGIN TRANSACTION;")

        # Check if any new messages have been added
        messages = db.execute("SELECT *, strftime('%d-%m', message_time) AS date, strftime('%H:%M', message_time) AS time FROM messages WHERE inbox_id = ? AND id > ? ORDER BY message_time ASC", inbox_id, data["last_message_id"])
        if not messages:
            db.execute("COMMIT;")
            return jsonify({"result": True, "new": False, "inbox_id": inbox_id}), 200

        # Else, we know we have new messages
        response = {
            "result": True,
            "new": True,
            "inbox_id": inbox_id,
            "last_message_id": messages[len(messages) - 1]["id"],
            "comment_list": list()
        }

        user1 = db.execute("SELECT id, fullname, username FROM users WHERE id = ?;", session["user_id"])
        user2 = db.execute("SELECT id, fullname, username FROM users WHERE id = ?;", data["person_id"])

        if not user2:
            raise Exception("User account not found!")

        for message in messages:
            if message["sender_id"] == session["user_id"]:
                fullname = user1[0]["fullname"]
                username = user1[0]["username"]
            else:
                fullname = user2[0]["fullname"]
                username = user2[0]["username"]

            message_info = {
                "fullname": fullname,
                "username": username,
                "owner": True if message["sender_id"] == session["user_id"] else False,
                "message_id": message["id"],
                "message_time": message["time"],
                "message_date": message["date"],
                "contents": escape(message["contents"])
            }
            print(message_info["contents"])
            response["comment_list"].append(message_info)
        db.execute("COMMIT;")
        return jsonify(response)
    except Exception as e:
        db.execute("ROLLBACK;")
        logging.error(f"Error: {e}")
        return jsonify({"result": False}), 400


# Delete messages
@app.route("/api/delete_message", methods=["POST"])
@login_required
def delete_message():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)

    data = request.get_json()
    print(data)

    if not data or not data.get("message_id"):
        return jsonify({"result": False}), 400

    info = db.execute("SELECT inbox_id, sender_id FROM messages WHERE id = ?;", data["message_id"])
    if info[0]["sender_id"] != session["user_id"]:
        return jsonify({"result": False}), 400

    try:
        db.execute("BEGIN TRANSACTION;")
        db.execute("UPDATE inbox SET messages = messages - 1 WHERE id = ?;", info[0]["inbox_id"])
        db.execute("INSERT INTO deleted_messages(inbox_id, message_id, sender_id) VALUES(?, ?, ?);", info[0]["inbox_id"], data["message_id"], session["user_id"])
        db.execute("DELETE FROM messages WHERE id = ?;", data["message_id"])
        db.execute("COMMIT;")
    except Exception as e:
        db.execute("ROLLBACK;")
        logging.error(f"Error: {e}")
        return jsonify({"result": False}), 400

    return jsonify({"result": True}), 200


# Search Page
@app.route("/search")
@login_required
def search():
    return render_template("search.html")


# Manage search queries
@app.route("/api/search", methods=["POST"])
@login_required
def search_q():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        abort(404)

    data = request.get_json()

    if not data or not data.get("target") or data["target"] not in ["users", "posts"] or not data.get("option") or data["option"] not in ["users_all", "users_friends", "posts_all", "posts_mine", "posts_friends"] or not data.get("query") or len(data["query"]) < 1 or len(data["query"]) > 640:
        return jsonify({"result": False}), 400

    # Search through users
    if data["target"] == "users":
        # Search through all
        if data["option"] == "users_all":
            users = db.execute("SELECT DISTINCT id, fullname, username, pfp_location FROM users WHERE username LIKE ? OR fullname LIKE ? ORDER BY username, fullname;", "%" + data["query"] + "%", "%" + data["query"] + "%")

        # Search through friends
        elif data["option"] == "users_friends":
           users = db.execute(
               """
               SELECT DISTINCT users.id, users.fullname, users.username, users.pfp_location
               FROM users
               JOIN friends
               ON ((users.id = friends.user_id1 AND friends.user_id2 = ?) OR (users.id = friends.user_id2 AND friends.user_id1 = ?))
               WHERE friends.friends = 1
               AND users.username LIKE ? OR users.fullname LIKE ?
               ORDER BY users.username, users.fullname;
               """,
               session["user_id"], session["user_id"], "%" + data["query"] + "%", "%" + data["query"] + "%"
            )

        # Invalid input
        else:
            return jsonify({"result": False}), 400

        # No search results
        if not users:
            return jsonify({"result": True, "found": False}), 200

        response = {
            "result": True,
            "found": True,
            "target": "users",
            "search_results": users
        }
    else:
        # Search through all
        if data["option"] == "posts_all":
            posts = db.execute("SELECT DISTINCT id, title, contents, imagelocation, likes, comments FROM posts WHERE title LIKE ? ORDER BY title;", "%" + data["query"] + "%")

        # Search through user's own
        elif data["option"] == "posts_mine":
            posts = db.execute("SELECT DISTINCT id, title, contents, imagelocation, likes, comments FROM posts WHERE user_id = ? AND title LIKE ? ORDER BY title;", session["user_id"], "%" + data["query"] + "%")

        # Search through user's friends'
        elif data["option"] == "posts_friends":
            posts = db.execute(
                """
                SELECT DISTINCT p.id, p.title, p.contents, p.imagelocation, p.likes, p.comments
                FROM posts as p
                JOIN friends AS f
                ON ((p.user_id = f.user_id1 AND f.user_id2 = ?) OR (p.user_id = f.user_id2 AND f.user_id1 = ?))
                WHERE f.friends = 1
                AND p.title LIKE ?
                ORDER BY p.title;
                """,
                session["user_id"], session["user_id"], "%" + data["query"] + "%"
            )
        # Invalid input
        else:
            return jsonify({"result": False}), 400

        # No results found
        if not posts:
            return jsonify({"result": True, "found": False}), 200

        # Add tags to every post
        for post in posts:
            post["contents"] = post["contents"][0:121] + "..." if len(post["contents"]) > 121 else post["contents"][0:121]
            tags = db.execute("SELECT DISTINCT i.interest AS tag FROM interests AS i JOIN post_tags AS p ON i.id = p.tag_id WHERE p.post_id = ? ORDER BY tag;", post["id"])
            post["tags"] = tags

        response = {
            "result": True,
            "found": True,
            "target": "posts",
            "search_results": posts
        }

    return jsonify(response)


# Permanently delete user account and data
@app.route("/remove_account", methods=["GET", "POST"])
@login_required
def remove_account():
    if request.method == "POST":
        password = request.form.get("password")
        user = db.execute("SELECT hash FROM users WHERE id = ?;", session["user_id"])
        if not password:
            return apology("Invalid Submission!")
        elif not check_password_hash(user[0]["hash"], password):
            return apology("Incorrect Password!")
        try:
            # Begin deletion of all user data
            db.execute("BEGIN TRANSACTION;")

            # Remove user from everyone's friendlist
            db.execute("UPDATE users SET friends = friends - 1 WHERE id IN (SELECT user_id2 FROM friends WHERE user_id1 = ? AND friends = 1);", session["user_id"])

            # Remove user from friends table
            db.execute("DELETE FROM friends WHERE user_id1 = ? OR user_id2 = ?;", session["user_id"], session["user_id"])

            # Delete all images from posts by user
            images = db.execute("SELECT imagelocation FROM posts WHERE user_id = ?;", session["user_id"])

            for image in images:
                if image["imagelocation"]:
                    try:
                        # Remove image (if located on server on server)
                        os.remove(image["imagelocation"])
                        directory = os.path.dirname(image["imagelocation"])

                        # Remove folder (if empty)
                        if os.path.exists(directory) and not os.listdir(directory):
                            os.removedirs(directory)
                    except OSError:
                        pass

            # Remove all posts by user including tags, interactions, comments and comment interactions
            db.execute("DELETE FROM post_tags WHERE post_id IN (SELECT DISTINCT id FROM posts WHERE user_id = ?);", session["user_id"])
            db.execute("DELETE FROM user_post_interactions WHERE user_id = ?;", session["user_id"])

            db.execute("DELETE FROM user_comment_interactions WHERE user_id = ?;", session["user_id"])
            db.execute("DELETE FROM comments WHERE user_id = ?;", session["user_id"])

            db.execute("DELETE FROM posts WHERE user_id = ?;", session["user_id"])

            # Remove all messages sent and recieved by user
            db.execute("DELETE FROM deleted_messages WHERE sender_id = ?;", session["user_id"])
            db.execute("DELETE FROM messages WHERE sender_id = ? OR recipient_id = ?;", session["user_id"], session["user_id"])
            db.execute("DELETE FROM inbox WHERE user_id1 = ? OR user_id2 = ?;", session["user_id"], session["user_id"])

            # Delete all user interests
            db.execute("DELETE FROM user_interests WHERE user_id = ?;", session["user_id"])

            # Delete user pfp
            pfp = db.execute("SELECT pfp_location FROM users WHERE id = ?;", session["user_id"])
            if pfp and pfp[0]["pfp_location"] != 'server_hosted_files/profile_pics/default_profile_pic/user_profile_pic.png':
                try:
                    os.remove(pfp[0]["pfp_location"])
                    pfp_dir = os.path.dirname(pfp[0]["pfp_location"])
                    os.removedirs(pfp_dir)
                except OSError:
                    pass

            # Delete remaining user data
            db.execute("DELETE FROM users WHERE id = ?;", session["user_id"])

            db.execute("COMMIT;")
            session.clear()
            return redirect("/welcome")
        except Exception as e:
            db.execute("ROLLBACK;")
            logging.error(f"An error occurred: {str(e)}")
            return apology(f"Account Deletion Failed! - {e}")
    else:
        return render_template("remove_account.html")


if __name__ == '__main__':
    app.run()
