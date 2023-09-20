from flask import redirect, render_template, session
from functools import wraps

# Render apology for any sort of invalid submission
def apology(message, code=400):
    return render_template("apology.html", code=str(code), message=message), code

# Decorator to make a path requiring login be inaccessible without login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/welcome")
        return f(*args, **kwargs)

    return decorated_function