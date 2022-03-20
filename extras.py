from functools import wraps
from flask import session, redirect, render_template


# Function to make user's login necessary
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function 

def error(error_text):
    return render_template("errorpage.html", error_text=error_text)