from flask import Flask, render_template, session, redirect, request
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
import sqlite3, os

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Define database name
app.config["DB_NAME"] = "database.db"

MAPS_API = os.getenv("MAPS-API")

# Configure session
Session(app)

@app.route("/")
def index():

    # Connect to database
    connection = sqlite3.connect(app.config["DB_NAME"])
    cursor = connection.cursor()

    # Query database for markers
    cursor.execute("SELECT photo, latitude, longitude, info FROM places")
    markers = cursor.fetchall()

    return render_template("index.html", len=len(markers), markers=markers, MAPS_API=MAPS_API)

@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    # If method is POST
    if request.method == "POST":

        # Connect to database
        connection = sqlite3.connect(app.config["DB_NAME"])
        cursor = connection.cursor()

        # Define user's credentials
        username = request.form.get("username")
        fullName = request.form.get("fullName")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        telephone = request.form.get("telephone")

        if not username or not fullName or not email or not telephone or not password or not confirmation:
            return "Please provide all details"

        # Check if password and confirm password do not match
        if password != confirmation:
            return "Passwords do not match"

        # Query database for username
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cursor.fetchall()

        # Check if username entered by user exists already in db.
        if len(rows) >= 1:
            return "Username already exists"

        # Define hashpassword
        hash_pw = generate_password_hash(password)

        # Insert new user into database
        cursor.execute("INSERT INTO users (username, hash, fullName, email, telephone) VALUES (?, ?, ?, ?, ?, ?)", (username, hash_pw, fullName, email, telephone))
        connection.commit()

        # Query database for username
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        rows = cursor.fetchall()
        
        # Save changes
        connection.commit()

        # Close connection to database
        cursor.close()
        connection.close()

        # Redirect user to login
        return redirect("/login")

    else:

        return render_template("register.html")

@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # If method is POST
    if request.method == "POST":

        # Connect to database
        connection = sqlite3.connect(app.config["DB_NAME"])
        cursor = connection.cursor()

        username = request.form.get("username")

        # Query database for username
        cursor.execute("SELECT id, hash FROM users WHERE username = ?", (username,))
        rows = cursor.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][1], request.form.get("password")):
            return "Invalid username and/or password"

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        session["username"] = username

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")