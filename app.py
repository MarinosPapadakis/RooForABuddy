from flask import Flask, render_template, session, redirect
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
import sqlite3

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Define database name
app.config["DB_NAME"] = "database.db"

# Configure session
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

