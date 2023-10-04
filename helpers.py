from flask import redirect, render_template, session
from functools import wraps
import string

# Render apology for any sort of invalid submission
def apology(message, code=400):
    return render_template("apology.html", code=str(code), message=message), code


# Decorator to make certain routes be inaccessible without login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/welcome")
        return f(*args, **kwargs)

    return decorated_function


# Check if a password has at least one lowercase alphabet, one uppercase alphabet, one number and one special character
def check_password(password):
    password = str(password)
    has_lower = has_upper = has_number = has_special = False
    if len(password) < 8:
        return False
    for char in password:
        if not has_lower and char in string.ascii_lowercase:
            has_lower = True
        if not has_upper and char in string.ascii_uppercase:
            has_upper = True
        if not has_number and char in string.digits:
            has_number = True
        if not has_special and char in string.punctuation:
            has_special = True
        if has_lower and has_upper and has_number and has_special:
            return True
    return False