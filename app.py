import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify, abort, send_file
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, apology
import random
import logging


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
        if not username or not fullname or not password1 or not password2 or password1 != password2 or len(fullname) > 70 or len(password1) < 8:
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

    # No username found
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
        if not friends:
            status = 0
        if friends:
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
@app.route("/manage_friends", methods=["GET", "POST"])
@login_required
def manage_friends():
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        id = request.form.get("user_id")
        if not id or not id.isdigit() or id == session["user_id"]:
            abort(404)

        id = int(id)
        try:
            db.execute("BEGIN TRANSACTION;")
            friends = db.execute("SELECT friends FROM friends WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], id)
            if not friends:
                db.execute("INSERT INTO friends(user_id1, user_id2, friends) VALUES(?, ?, 2);", session["user_id"], id)
                db.execute("INSERT INTO friends(user_id1, user_id2, friends) VALUES(?, ?, 3);", id, session["user_id"])
                db.execute("COMMIT;")
                return jsonify({"result": "Request Sent"}), 200
            elif friends[0]["friends"] == 0:
                db.execute("UPDATE friends SET friends = 2 WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], id)
                db.execute("UPDATE friends SET friends = 3 WHERE user_id1 = ? AND user_id2 = ?;", id, session["user_id"])
                db.execute("COMMIT;")
                return jsonify({"result": "Request Sent"}), 200
            else:
                db.execute("UPDATE friends SET friends = 0 WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], id)
                db.execute("UPDATE friends SET friends = 0 WHERE user_id1 = ? AND user_id2 = ?;", id, session["user_id"])
                db.execute("DELETE FROM friends WHERE friends = 0;")

                if friends[0]["friends"] == 1:
                    db.execute("UPDATE users SET friends = friends - 1 WHERE id = ? OR id = ?;", session["user_id"], id)

                db.execute("COMMIT;")
                return jsonify({"result": "Removed Friend"}), 200
        except Exception as e:
            db.execute("ROLLBACK;")
            return apology("Friend could not be added/removed!")
    else:
        abort(404)


# Handles Accept Requests
@app.route("/accept_friend_request", methods=["GET", "POST"])
def accept_friend_request():
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        friend_id = request.form.get("user_id")
        if not friend_id or friend_id == session["user_id"]:
            abort(404)

        friend_id = int(friend_id)

        try:
            db.execute("BEGIN TRANSACTION;")

            # Check for validity of request
            status = db.execute("SELECT friends FROM friends WHERE user_id1 = ? AND user_id2 = ?;", session["user_id"], friend_id)
            if not status or status[0]["friends"] != 3:
                db.execute("ROLLBACK;")
                return jsonify({"result": False})

            db.execute(
                "UPDATE friends SET friends = 1 WHERE (user_id1 = ? AND user_id2 = ?) OR (user_id1 = ? AND user_id2 = ?);"
                , session["user_id"], friend_id, friend_id, session["user_id"]
            )
            db.execute("UPDATE users SET friends = friends + 1 WHERE id = ? OR id = ?;", session["user_id"], friend_id)
            db.execute("COMMIT;")
            return jsonify({"result": True})

        except Exception as e:
            db.execute("ROLLBACK;")
            return jsonify({"result": False})

    else:
        abort(404)


# Manage Profile Settings
@app.route("/profile_settings", methods=["GET", "POST"])
@login_required
def profile_settings():
    if request.method == "POST":
        fullname = request.form.get("name")
        about_me = request.form.get("about_me")
        interest_list = request.form.getlist("interest")

        if not fullname or len(fullname) > 70 or len(about_me) > 640:
            return apology("Invalid Submission!")

        db.execute("UPDATE users SET fullname = ?, about_me = ? WHERE id = ?;", fullname, about_me, session["user_id"])
        db.execute("DELETE FROM user_interests WHERE user_id = ?;", session["user_id"])

        if interest_list:
            db.execute("BEGIN TRANSACTION;")
            for interest in interest_list:
                if interest in list_of_interests:
                    interest_id = db.execute("SELECT id FROM interests WHERE interest = ?;", interest)
                    db.execute("INSERT INTO user_interests(user_id, interest_id) VALUES(?, ?);", session["user_id"], interest_id[0]["id"])
                else:
                    db.execute("ROLLBACK;")
                    return apology("Invalid Submission!")
            db.execute("COMMIT;")

        return redirect("/profile")
    else:
        user = db.execute("SELECT fullname, about_me FROM users WHERE id = ?;", session["user_id"])
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


# Friends Page
@app.route("/friends")
@login_required
def friends():
    friends = db.execute("SELECT DISTINCT id, username, fullname FROM users WHERE id IN (SELECT user_id2 FROM friends WHERE user_id1 = ? AND friends = 1);", session["user_id"])
    requests = db.execute("SELECT DISTINCT id, username, fullname FROM users WHERE id IN (SELECT user_id2 FROM friends WHERE user_id1 = ? AND friends = 3);", session["user_id"])
    recommendations = db.execute(
        """
        SELECT DISTINCT u.id AS id, u.username AS username, u.fullname AS fullname
        FROM users u
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


@app.route("/posts", methods=["GET", "POST"])
@login_required
def posts():
    if request.method == "POST":
        ...
    else:
        my_posts = db.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY post_time DESC;", session["user_id"])
        for post in my_posts:
            tag_list = list()
            tags = db.execute("SELECT interests.interest AS tag FROM interests JOIN post_tags ON post_tags.tag_id = interests.id WHERE post_id = ? ORDER BY tag;", post["id"])
            for tag in tags:
                tag_list.append(tag["tag"])
            post["tags"] = tag_list

            # Set user_post_interaction status - 0 for no interaction, 1 for liked, 2 for disliked
            interaction_status = db.execute("SELECT status FROM user_post_interactions WHERE post_id = ? AND user_id = ?;", post["id"], session["user_id"])
            post["status"] = 0 if not interaction_status else interaction_status[0]["status"]

        user = db.execute("SELECT fullname, username FROM users WHERE id = ?;", session["user_id"])

        return render_template("posts.html", my_posts=my_posts, my_name=user[0]["fullname"], my_username=user[0]["username"])


# Allows users to create posts
@app.route("/createpost", methods=["GET", "POST"])
@login_required
def post():
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
            post_id = db.execute("INSERT INTO posts(user_id, title, contents, post_time) VALUES(?, ?, ?, CURRENT_TIMESTAMP);" , session["user_id"], title, contents)

            # Increase post count for user
            db.execute("UPDATE users SET posts = posts + 1 WHERE id = ?;", session["user_id"])

            # If image was uploaded
            if image and image != "":

                # Sanitize and validate input
                image.filename = secure_filename(image.filename).lower()
                print(image.filename)
                if not image.filename.endswith(".png") and not image.filename.endswith(".jfif") and not image.filename.endswith(".pjp") and not image.filename.endswith(".jpg") and not image.filename.endswith(".jpeg") and not image.filename.endswith(".pjpeg"):
                    raise Exception("Invalid Image Format!")

                # Save image in server
                imagelocation = os.path.join("server_hosted_files", "posts", str(post_id))
                if not os.path.exists(imagelocation):
                    os.makedirs(imagelocation)
                imagelocation = os.path.join(imagelocation, str(image.filename))
                image.save(imagelocation)
                db.execute("UPDATE posts SET imagelocation = ? WHERE id = ?;", imagelocation, post_id)

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


# Manage post likes/dislikes
@app.route("/manage_likes", methods=["GET", "POST"])
@login_required
def manage_likes():
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
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
    else:
        abort(404)


# Delete posts (via AJAX)
@app.route("/delete_post", methods=["GET", "POST"])
@login_required
def delete_post():
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        post_id = request.form.get("post_id")
        if not post_id or post_id == "":
            return jsonify({"result": False})
        user_id = db.execute("SELECT user_id FROM posts WHERE id = ?;", post_id)

        if user_id[0]["user_id"] != session["user_id"]:
            return jsonify({"result": False})

        try:
            db.execute("BEGIN TRANSACTION;")

            # Decrease post count
            db.execute("UPDATE users SET posts = posts - 1 WHERE id = ?;", session["user_id"])

            # Remove carnival points gained from posts
            info = db.execute("SELECT likes, comments FROM posts WHERE id = ?;", post_id)
            decrement = int(info[0]["likes"]) * 2 + int(info[0]["comments"]) * 5
            db.execute("UPDATE users SET carnival = carnival - ? WHERE id = ?;", decrement, session["user_id"])

            # Delete tags
            db.execute("DELETE FROM post_tags WHERE post_id = ?;", post_id)

            # Delete user-post interaction status
            db.execute("DELETE FROM user_post_interactions WHERE post_id = ?;", post_id)

            # Delete server hosted file
            image = db.execute("SELECT imagelocation FROM posts WHERE id = ?;", post_id)
            if image[0]["imagelocation"]:
                try:
                    # Remove image
                    os.remove(image[0]["imagelocation"])
                    directory = os.path.dirname(image[0]["imagelocation"])

                    # Remove folder (if empty)
                    if not os.listdir(directory):
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
    else:
        abort(404)


# Permanently delete user account and data
@app.route("/remove_account", methods=["GET", "POST"])
@login_required
def remove_account():
    if request.method == "POST":
        password = request.form.get("password")
        user = db.execute("SELECT hash FROM users WHERE id = ?;", session["user_id"])
        confirm = request.form.get("confirmation")
        if not password or not confirm:
            return apology("Invalid Submission!")
        elif not check_password_hash(user[0]["hash"], password):
            return apology("Incorrect Password!")
        elif confirm == "No":
            return redirect("/account_settings")
        elif confirm == "Yes" and check_password_hash(user[0]["hash"], password):
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
                            # Remove image
                            os.remove(image["imagelocation"])
                            directory = os.path.dirname(image["imagelocation"])

                            # Remove folder (if empty)
                            if not os.listdir(directory):
                                os.removedirs(directory)
                        except OSError:
                            pass

                # Remove all posts by user including tags and interactions
                db.execute("DELETE FROM post_tags WHERE post_id IN (SELECT DISTINCT id FROM posts WHERE user_id = ?);", session["user_id"])
                db.execute("DELETE FROM user_post_interactions WHERE post_id IN (SELECT DISTINCT id FROM posts WHERE user_id = ?);", session["user_id"])
                db.execute("DELETE FROM posts WHERE user_id = ?;", session["user_id"])

                # Delete all user interests
                db.execute("DELETE FROM user_interests WHERE user_id = ?;", session["user_id"])

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
            return apology("Invalid Submission!")
    else:
        return render_template("remove_account.html")


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', threaded=True)