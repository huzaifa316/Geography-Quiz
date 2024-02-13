import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from random import randint

from helpers import login_required, apology, admin_required, generate_image

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///geog.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    raw = db.execute("SELECT questions, correct, level FROM users WHERE id = ?", session["user_id"])
    return render_template("index.html", questions=raw[0]["questions"], correct=raw[0]["correct"], level=int(raw[0]["level"]))


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    username = request.form.get('username')
    if request.method == "GET":
        return render_template("login.html")
    else:
        if not username:
            return apology("Invalid username", 403)
        elif not request.form.get("password"):
            return apology("Invalid Password", 403)

        username = request.form.get('username').lower()
        raw = db.execute("SELECT id, username, hash FROM users WHERE(username = ?)", username)

        if len(raw) != 1 or check_password_hash(raw[0]["hash"], request.form.get("password")):
            session["user_id"] = int(raw[0]["id"])
            return redirect("/")
        else:
            return apology("Invalid Username or Password", 403)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username").lower()
        if not username or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Invalid Username or Password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match", 400)

        raw = db.execute("SELECT username FROM users WHERE username = ?", username)

        if len(raw) > 1:
            return apology("Username already exists", 400)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username,
                   generate_password_hash(request.form.get("password")))

        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


ques = 0
user = {}
level = 0
num = 0
id = 0
@app.route("/quiz", methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == "GET":
        global ques
        global level
        global num
        global id
        if ques <= num:
            raw = db.execute("SELECT question, id, image FROM questions WHERE level = ? AND id != ?", level + 1, id)
            row = randint(0, (len(raw) - 1))
            question = raw[row]["question"]
            id = raw[row]["id"]
            image = raw[row]["image"]
            if randint(0, 1) == 0:
                ques += 1
                return render_template("quiz.html", question=question, image=image, id=id, button="n")
            else:
                raw = db.execute("SELECT answer, wrong FROM questions WHERE id = ?", id)
                right = raw[0]["answer"].title()
                wrong, wrong1 = str(raw[0]["wrong"]).split(", ")
                if randint(0, 2) == 0:
                    ques += 1
                    return render_template("button.html", question=question, image=image, id=id, answer1=right, answer2=wrong1.title(), answer3=wrong.title(), button="y")
                elif randint(0, 2) == 1:
                    ques += 1
                    return render_template("button.html", question=question, image=image, id=id, answer1=wrong.title(), answer2=right, answer3=wrong1.title(), button="y")
                else:
                    ques += 1
                    return render_template("button.html", question=question, image=image, id=id, answer1=wrong1.title(), answer2=wrong.title(), answer3=right, button="y")
        else:
            total = 0
            html = ''
            for key in user.keys():
                if user[key] == 'y':
                    raw = db.execute("SELECT question, level FROM questions WHERE id = ?", key)
                    html += '<h3>' + raw[0]['question'] + ' : <span class="green">Correct!</span></h3><br></br>'
                    db.execute("UPDATE users SET questions = questions + 1 WHERE id = ?", session["user_id"])
                    db.execute("UPDATE users SET correct = correct + 1 WHERE id = ?", session["user_id"])
                    total += 1
                else:
                    raw = db.execute("SELECT question, level, answer FROM questions WHERE id = ?", key)
                    html += '<h3>' + \
                        raw[0]['question'] + ' : <span class="red">Incorrect!</span><br></br> <span class="green">Correct: </span>' + \
                        raw[0]["answer"] + '</h3><br></br>'
                    raw = db.execute("SELECT level FROM users WHERE id = ?", session["user_id"])
                    if level > int(raw[0]["level"]):
                        level = level
                    else:
                        level = int(raw[0]["level"])

                    db.execute("UPDATE users SET questions = questions + 1, level = ? WHERE id = ?", level, session["user_id"])

            user.clear()
            level = 0
            ques = 0
            return render_template("final.html", body=html, percent=int(round(((total)/num) * 100)))
    else:
        id = request.form.get("id")

        if request.form.get("button") == "y":
            answer = request.form["submit_button"]
        else:
            answer = request.form.get("answer")

        raw = db.execute("SELECT answer FROM questions WHERE id = ?", id)
        if len(raw) > 1:
            return apology("error", 400)

        if str(raw[0]["answer"]).lower().strip() == answer.lower().strip():
            user[id] = 'y'
            if level < 8:
                level += 1
            return redirect("/quiz")
        else:
            user[id] = 'n'
            if level > 1:
                level -= 1
            return redirect("/quiz")



@app.route("/leaderboard", methods=['GET', 'POST'])
@login_required
def leaderboard():
    names = []
    i = 1
    raw = db.execute("SELECT username, questions, correct, level FROM users ORDER BY correct DESC")
    for name in raw:
        if name["username"] != "admin":
            stats = {}
            stats["position"] = i
            stats["name"] = name["username"].title()
            stats["questions"] = name["questions"]
            stats["correct"] = name["correct"]
            stats["level"] = name["level"]

            names.append(stats)
            i += 1

    one = names[0]["name"]
    raw = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = raw[0]["username"]

    for name in names:
        if name["name"] == username.title():
            yours = name["position"]
            break
    else:
        return apology("User not found", 400)

    return render_template("leaderboard.html", leaderboard=names, one=one.title(), urname=username.title(), yours=yours)


@app.route("/all", methods=['GET', 'POST'])
@login_required
def questions():
    questions = []
    raw = db.execute("SELECT id, question, level FROM questions ORDER BY level ASC")
    for question in raw:
        values = {}
        values["id"] = question["id"]
        values["question"] = question["question"]
        values["level"] = question["level"]

        questions.append(values)

    return render_template("questions.html", questions=questions)


@app.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    if request.method == "GET":
        return render_template("add.html")
    else:
        if not request.form.get("question") or not request.form.get("answer") or not request.form.get("wrong") or not request.form.get("level") or not request.form.get("word") or int(request.form.get("level")) > 9 or int(request.form.get("level")) < 1:
            return apology("Invalid", 400)
        try:
            one, two = request.form.get("wrong").split(", ")
        except ValueError:
            return apology("Invalid", 400)

        db.execute("INSERT INTO review (question, answer, wrong, level, word) VALUES(?, ?, ?, ?, ?)", request.form.get("question"), request.form.get("answer"), request.form.get("wrong"), int(request.form.get("level")), request.form.get("word"))
        return redirect("/")


@app.route("/approve", methods=['GET', 'POST'])
@admin_required
def approve():
    if request.method == "GET":
        questions = []
        raw = db.execute("SELECT id, question, level FROM review ORDER BY level ASC")
        for question in raw:
            values = {}
            values["id"] = question["id"]
            values["question"] = question["question"]
            values["level"] = question["level"]

            questions.append(values)

        return render_template("approve.html", questions=questions)
    else:
        if request.form.get("id") == "deny":
            db.execute("DELETE FROM review")
        else:
             if len(raw) < 1:
                 return apology("Invalid response", 400)
             raw = db.execute("SELECT * FROM review WHERE id = ?", int(request.form.get("id")))
             db.execute("INSERT INTO questions (question, answer, wrong, level, image) VALUES(?, ?, ?, ?, ?)", raw[0]["question"], raw[0]["answer"], raw[0]["wrong"], int(raw[0]["level"]), generate_image(raw[0]["word"]))
             db.execute("DELETE FROM review WHERE id = ?", int(request.form.get("id")))

        return redirect("/")


@app.route("/no", methods=['GET', 'POST'])
@login_required
def no():
    if request.method == "GET":
        return render_template("no.html")
    else:
        global num
        if not request.form.get("no"):
            num = 9
            return redirect("/quiz")
        
        try:
            int(request.form.get("no"))
        except ValueError:
            num = 9
            return redirect("/quiz")
        
        num = int(request.form.get("no")) - 1
        if num < 1:
            num = 9
        return redirect("/quiz")

