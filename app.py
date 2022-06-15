import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import pandas as pd


from helpers import login_required, apology

# Configure Application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///reflexion.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        rating = request.form.get("rating")
        reflection = request.form.get("reflection")

        try:
            rating = int(request.form.get("rating"))
        except:
            return render_template("apology.html", text = "Rating must be a positive integer.")

        if int(rating) < 0:
            return render_template("apology.html", text = "Rating must be a positive integer amount only.")

        # Calculating how much it would cost one to buy their preferred number of shares.
        user_id = session["user_id"]

        # Current time
        time = datetime.datetime.now()
        time_1 = int(time.strftime("%Y%m%d%H%M"))

        db.execute("INSERT INTO diary (user_id, rating, reflection, time_1, time) VALUES (?, ?, ?, ?, ?)", user_id, rating, reflection, time_1, time)
        return render_template("index.html")


@app.route("/diary")
@login_required
def diary():
    user_id = session["user_id"]
    history = db.execute("SELECT * FROM diary WHERE user_id = (?)", user_id)
    return render_template("diary.html", history=history)

@app.route("/line")
@login_required
def line():
    user_id = session["user_id"]
    data = db.execute("SELECT * FROM diary WHERE user_id = (?)", user_id)
    df = pd.DataFrame(data)
    try:
        df = df.drop(columns=['reflection', 'user_id'], axis=1)
        times=list(df["time"])
        ratings = list(df['rating'])
    except:
        return render_template("apology.html", text="You don't have any data yet!")
    for_bar = ["0 - 10", "11 - 20", "21 - 30", "31 - 40", "41 - 50", "51 - 60", "61 - 71", "81 - 90", "91 - 100"]
    frequency = [0,0,0,0,0,0,0,0,0,0]

    # plt.style.use('seaborn-darkgrid')
    # plt.figure(figsize=(20,5))
    # plt.title('Happiness vs Time')
    # plt.plot(df['time_1'], df['rating'], 'b-o')
    # plt.xlabel('Time')
    # plt.ylabel('Rating')
    # plt.grid(True)
    # plt.savefig('new_plot.jpg')
    return render_template("line.html", times=times, ratings=ratings)

@app.route("/pie")
@login_required
def pie():
    user_id = session["user_id"]
    data = db.execute("SELECT * FROM diary WHERE user_id = (?)", user_id)
    df = pd.DataFrame(data)
    try:
        df = df.drop(columns=['reflection', 'user_id'], axis=1)
        times=list(df["time"])
        ratings = list(df['rating'])
    except:
        return render_template("apology.html", text="You don't have any data yet!")
    good=0
    bad=0
    for rating in ratings:
        if rating >= 50:
            good = good+1
        else:
            bad=bad+1

    good_bad = ["Good", "Bad"]
    numbers = [good, bad]
    return render_template("pie.html", ratings=ratings, times=times, good_bad=good_bad, numbers=numbers)



@app.route("/bar")
@login_required
def bar():
    user_id = session["user_id"]
    data = db.execute("SELECT * FROM diary WHERE user_id = (?)", user_id)
    df = pd.DataFrame(data)
    try:
        df = df.drop(columns=['reflection', 'user_id'], axis=1)
        times=list(df["time"])
        ratings = list(df['rating'])
    except:
        return render_template("apology.html", text="You don't have any data yet!")

    for_bar = ["0 - 10", "11 - 20", "21 - 30", "31 - 40", "41 - 50", "51 - 60", "61 - 71", "71 - 81", "81 - 90", "91 - 100"]
    frequency = [0,0,0,0,0,0,0,0,0,0]

    for rating in ratings:
        if rating > 0 and rating < 11:
            frequency[0]+=1
        elif rating >= 11 and rating < 21:
            frequency[1]+=1
        elif rating >= 21 and rating < 31:
            frequency[2]+=1
        elif rating >= 31 and rating < 41:
            frequency[3]+=1
        elif rating >= 41 and rating < 51:
            frequency[4]+=1
        elif rating >= 51 and rating < 61:
            frequency[5]+=1
        elif rating >= 61 and rating < 71:
            frequency[6]+=1
        elif rating >= 71 and rating < 81:
            frequency[7]+=1
        elif rating >= 81 and rating < 91:
            frequency[8]+=1
        elif rating >= 91 and rating <= 100:
            frequency[9]+=1

    return render_template("bar.html", frequency=frequency, for_bar=for_bar)


@app.route("/clear", methods=['GET','POST'])
@login_required
def clear():
    if request.method == "GET":
        return redirect("/")
    else:
        user_id = session["user_id"]
        db.execute("DELETE FROM diary WHERE user_id = (?)", user_id)
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", text = "must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", text = "must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", text = "invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return render_template("apology.html", text = "Username field cannot be blank")
        if not password:
            return render_template("apology.html", text = "Password field cannot be blank")
        if not confirmation:
            return render_template("apology.html", text = "Confirm your password by entering it again")

        if confirmation != password:
            return render_template("apology.html", text = "Passwords must match.")

        numbers = ['0', '1','2','3','4','5','6','7','8','9']
        symbols = ['!','@','#','$','%','^','&','*','*']

        num_exists = 0
        symbol_exists = 0
        for number in numbers:
            if number in password:
                num_exists += 1
        for symbol in symbols:
            if symbol in password:
                symbol_exists += 1

        if num_exists < 1:
            return render_template("apology.html", text="Your Password must include at least one number")
        if symbol_exists < 1:
            return render_template("apology.html", text="Your Password must include at least one special symbol")

        hashed = generate_password_hash(password, method = 'pbkdf2:sha256', salt_length = 8)

        # Checking if the username already exists. Exists = 1 means that it does, exists = 0 means that it doesn't
        username = request.form.get("username")
        exists = db.execute("SELECT username FROM users WHERE username = ?", username)

        if len(exists) == 0:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed)
            return redirect("/")
        else:
            return render_template("apology.html", text = "It looks like this username already exists.")


# CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);
# CREATE TABLE sqlite_sequence(name,seq);
# CREATE UNIQUE INDEX username ON users (username);
# CREATE TABLE diary (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, rating INTEGER NOT NULL, reflection TEXT NOT NULL, time_1 INTEGER NOT NULL, time TEXT NOT NULL);