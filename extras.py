from functools import wraps
from flask import session, redirect


# Function to make user's login necessary
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
  g  def decorated_function(*ars, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)