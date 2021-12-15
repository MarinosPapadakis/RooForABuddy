from flask import Flask, render_template, session, redirect, request
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session
from flask_mail import Mail, Message 
from extras import login_required
import sqlite3, os, random

# Configure application
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET-KEY")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True

# Define database name
app.config["DB_NAME"] = "database.db"

app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".jpeg"]
app.config["UPLOAD_PATH"] = "static/uploads"

app.config["MAIL_SERVER"]= os.getenv("MAIL-SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL-PORT")
app.config["MAIL_USERNAME"] = os.getenv("MAIL-USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL-PASSWORD")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

# Get Google MAP API from host
MAPS_API = os.getenv("MAPS-API")

# Get Google MAP ID from host
MAP_ID = os.getenv("MAP-ID")

# Configure session
Session(app)

mail = Mail(app)

@app.route("/")
def index():

    # Connect to database
    connection = sqlite3.connect(app.config["DB_NAME"])
    cursor = connection.cursor()

    # Query database for markers
    cursor.execute("SELECT photo, latitude, longitude, info FROM foundAnimals")
    markers = cursor.fetchall()

    return render_template("index.html", len=len(markers), markers=markers, MAPS_API=MAPS_API, MAP_ID=MAP_ID)

@app.route("/lostpets")
def lostPets():

    # Connect to database
    connection = sqlite3.connect(app.config["DB_NAME"])
    cursor = connection.cursor()

    tels = []

    # Query database for pets
    cursor.execute("SELECT userId, photo, location, info info FROM foundAnimals")
    pets = cursor.fetchall()

    for i in range(len(pets)):
        
        cursor.execute("SELECT tel FROM users WHERE id=?", (pets[i][0],))
        tels.append(cursor.fetchall()[0][0])

    return render_template("index.html", len=len(pets), pets=pets, tels=tels)

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
        cursor.execute("INSERT INTO users (username, hash, fullName, email, tel) VALUES (?, ?, ?, ?, ?)", (username, hash_pw, fullName, email, telephone))
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
@login_required
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

@app.route("/foundanimal", methods=["GET", "POST"])
@login_required
def foundanimal():

    # If method is POST
    if request.method == "POST":

        # Connect to database
        connection = sqlite3.connect(app.config["DB_NAME"])
        cursor = connection.cursor()

        # Define user's credentials
        photo = request.files["file"]
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        info = request.form.get("info")

        # Secure filename
        filename = secure_filename(photo.filename)

        if filename != "":

            # Get file extension
            file_ext = os.path.splitext(filename)[1]

            # Check for valid extensions
            if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                return ("Error! Not accepted file extension")

            uPath = app.config["UPLOAD_PATH"]

            upPath = f"{uPath}/{filename}"

            # Insert new pet into database
            cursor.execute("INSERT INTO foundAnimals (userId, photo, latitude, longitude, info) VALUES (?, ?, ?, ?, ?)", (session["user_id"], upPath, latitude, longitude, info))
            connection.commit()

            # Save file
            photo.save(upPath)

            # Close connection to database
            cursor.close()
            connection.close()

        # Redirect user to login
        return redirect("/")

    else:

        return render_template("foundanimal.html")

@app.route("/lostpet", methods=["GET", "POST"])
@login_required
def lostpet():

    # If method is POST
    if request.method == "POST":

        # Connect to database
        connection = sqlite3.connect(app.config["DB_NAME"])
        cursor = connection.cursor()

        # Define user's credentials
        photo = request.files["file"]
        location = request.form.get("location")
        info = request.form.get("info")

        # Secure filename
        filename = secure_filename(photo.filename)

        if filename != "":

            # Get file extension
            file_ext = os.path.splitext(filename)[1]

            # Check for valid extensions
            if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                return ("Error! Not accepted file extension")

            uPath = app.config["UPLOAD_PATH"]

            upPath = f"{uPath}/{filename}"

            # Insert new pet into database
            cursor.execute("INSERT INTO lostPets (userId, location, photo, info) VALUES (?, ?, ?, ?)", (session["user_id"], location, upPath, info))
            connection.commit()

            # Save file
            photo.save(upPath)

            # Close connection to database
            cursor.close()
            connection.close()

        # Redirect user to login
        return redirect("/")

    else:

        return render_template("lostpet.html")

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():

    # If request method is POST
    if request.method == "POST":

        # Connect to database
        connection = sqlite3.connect(app.config["DB_NAME"])
        cursor = connection.cursor()

        # Define user id
        userid = session["user_id"]

        # Get post information
        oldpassword = request.form.get("oldpassword")
        newpassword = request.form.get("newpassword")
        confirmation = request.form.get("confirmation")

        # Check if passswords match
        if newpassword != confirmation:
            return("Passwords do not match")

        # Get user's hash
        cursor.execute("SELECT hash FROM users WHERE id=?", (userid, ))
        oldhash = cursor.fetchall()[0][0]

        # Check if old password matches
        if not check_password_hash(oldhash, oldpassword):
            return("Incorrect old password")

        # Generate new hash
        newhash = generate_password_hash(newpassword)

        # Update user's hash
        cursor.execute("UPDATE users SET hash = ? WHERE id = ?", (newhash, userid))
        connection.commit()

        # Close connection to the database
        cursor.close()
        connection.close()

        return redirect("/login")

    else:
        return render_template("changepassword.html")

@app.route("/changeemail", methods=["GET", "POST"])
@login_required
def changeemail():


    # If request method is POST
    if request.method == "POST":

        # Connect to database
        connection = sqlite3.connect(app.config["DB_NAME"])
        cursor = connection.cursor()

        # Check if pin is correct
        if int(request.form.get("pin")) != session["CHANGE_PASSWORD_PIN"]:
            return("Wrong pin")
        # Update email
        else:
            cursor.execute("UPDATE users SET email=? WHERE id=?", (request.form.get("newemail"), session["user_id"]))
            connection.commit()
        
        # Close connection to database
        cursor.close()
        connection.close()

        return redirect("/login")

    else:

        # Generate pin
        session["CHANGE_PASSWORD_PIN"] = int(random.randint(999, 9999))

        # Connect to database
        connection = sqlite3.connect(app.config["DB_NAME"])
        cursor = connection.cursor()

        # Get user pin
        pin = session["CHANGE_PASSWORD_PIN"]

        # Get user's current email
        cursor.execute("SELECT email FROM users WHERE id=?", (session["user_id"],))
        currentEmail = cursor.fetchall()[0][0]

        msg = Message("RooForABuddy Password Change", sender=app.config["MAIL_USERNAME"], recipients=[currentEmail])
        msg.body = f"{pin}\n If you did not request this change you should change your password immediately."
        mail.send(msg)

        # Close connection to database
        cursor.close()
        connection.close()

        return render_template("changeemail.html", currentEmail=currentEmail)

@app.route("/changetelephone", methods=["GET", "POST"])
@login_required
def changetelephone():

    # If request method is POST
    if request.method == "POST":

        # Connect to database
        connection = sqlite3.connect(app.config["DB_NAME"])
        cursor = connection.cursor()

        # Define user id
        userid = session["user_id"]

        # Get post information
        newTelephone = request.form.get("newtelephone")

        # Update user's hash
        cursor.execute("UPDATE users SET tel = ? WHERE id = ?", (newTelephone, userid))
        connection.commit()

        # Close connection to the database
        cursor.close()
        connection.close()

        return redirect("/")

    else:
        return render_template("changetelephone.html")