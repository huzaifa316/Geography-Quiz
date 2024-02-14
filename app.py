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
        #ensures username is lowered as that is how the usernames are stored
        username = request.form.get('username').lower()
        raw = db.execute("SELECT id, username, hash FROM users WHERE(username = ?)", username)

        if len(raw) == 1 and check_password_hash(raw[0]["hash"], request.form.get("password")):
            #set user id
            session["user_id"] = int(raw[0]["id"])

            #initialise quiz variables
            session["ques"] = 0
            session["user"] = []
            session["level"] = 0
            session["num"] = 0
            return redirect("/")
        else:
            return apology("Invalid Username or Password", 403)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        #sets username to local copy
        username = request.form.get("username")
        #checks if any field is blank
        if not username or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Invalid Username or Password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match", 400)
        #lowers the username so username case doesnt matter
        username = request.form.get("username").lower()
        raw = db.execute("SELECT username FROM users WHERE username = ?", username)

        if len(raw) > 0:
            return apology("Username already exists", 400)
        #hashes password and adds into database
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


#sets id to be acessible by all functions
id = 0
@app.route("/quiz", methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == "GET":
        #configures to use global id instead of local copy
        global id
        #session num initialised by num function - checks if function was skipped and sets default value of 10
        if not session["num"]:
            session["num"] == 10

        if session["ques"] <= session["num"]:
            #level is set to 0 by deafault by login - level increases with correctly answered questions
            #id != id ensures that questions are not repeated
            raw = db.execute("SELECT question, id, image FROM questions WHERE level = ? AND id != ?", session["level"] + 1, id)
            row = randint(0, (len(raw) - 1))
            question = raw[row]["question"]
            id = raw[row]["id"]
            image = raw[row]["image"]
            #randomly decides wheteher the question is multiple choice
            if randint(0, 1) == 0:
                #increments the number of questions asked
                session["ques"] += 1
                return render_template("quiz.html", question=question, image=image, id=id, button="n")
            else:
                #id variable set to the id of the last question asked
                raw = db.execute("SELECT answer, wrong FROM questions WHERE id = ?", id)
                right = raw[0]["answer"].title()
                #splits the 2 wrong answers in the database
                wrong, wrong1 = str(raw[0]["wrong"]).split(", ")
                #randomises the correct answer location
                if randint(0, 2) == 0:
                    session["ques"] += 1
                    return render_template("button.html", question=question, image=image, id=id, answer1=right, answer2=wrong1.title(), answer3=wrong.title(), button="y")
                elif randint(0, 2) == 1:
                    session["ques"] += 1
                    return render_template("button.html", question=question, image=image, id=id, answer1=wrong.title(), answer2=right, answer3=wrong1.title(), button="y")
                else:
                    session["ques"] += 1
                    return render_template("button.html", question=question, image=image, id=id, answer1=wrong1.title(), answer2=wrong.title(), answer3=right, button="y")
        else:
            #executes when quiz is finished
            total = 0
            html = ''
            for ans in session["user"]:
                #inserts html directly into jinja template
                key = list(ans.keys())[0]
                if ans[key] == 'y':
                    raw = db.execute("SELECT question, level FROM questions WHERE id = ?", key)
                    html += '<h3>' + raw[0]['question'] + ' : <span class="green">Correct!</span></h3><br></br>'
                    db.execute("UPDATE users SET questions = questions + 1 WHERE id = ?", session["user_id"])
                    db.execute("UPDATE users SET correct = correct + 1 WHERE id = ?", session["user_id"])
                    total += 1
                elif ans[key] == 'n':
                    raw = db.execute("SELECT question, level, answer FROM questions WHERE id = ?", key)
                    html += '<h3>' + \
                        raw[0]['question'] + ' : <span class="red">Incorrect!</span><br></br> <span class="green">Correct: </span>' + \
                        raw[0]["answer"] + '</h3><br></br>'
                    raw = db.execute("SELECT level FROM users WHERE id = ?", session["user_id"])
                    if session["level"] > int(raw[0]["level"]):
                        session["level"] = session["level"]
                    else:
                        session["level"] = int(raw[0]["level"])
                    #adds values to the database
                    db.execute("UPDATE users SET questions = questions + 1, level = ? WHERE id = ?", session["level"], session["user_id"])

            session["user"] = []
            session["level"] = 0
            session["ques"] = 0
            return render_template("final.html", body=html, percent=int(round(((total)/(session["num"] + 1)) * 100)))
    else:
        #executes on POST - checks if answer is correct and updates in a local dictionary stored in the users session
        id = request.form.get("id")

        if request.form.get("button") == "y":
            answer = request.form["submit_button"]
        else:
            answer = request.form.get("answer")

        raw = db.execute("SELECT answer FROM questions WHERE id = ?", id)
        if len(raw) > 1:
            return apology("error", 400)
        
        check = {}
        if str(raw[0]["answer"]).lower().strip() == answer.lower().strip():
            check[id] = 'y'
            if session["level"] < 9:
                session["level"] += 1
            session["user"].append(check)
        if str(raw[0]["answer"]).lower().strip() != answer.lower().strip():
            check[id] = 'n'
            session["level"] = session["level"] - 1
            if session["level"] < 1:
                session["level"] = 1
            session["user"].append(check)

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
    #allows users add questions - are added to different database so they can be reviewed - basic format checking performed
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
    #displays questions that need to be checked
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
    #gets numbe of questions user wants to be asked
    if request.method == "GET":
        return render_template("no.html")
    else:
        if not request.form.get("no"):
            session["num"] = 9
            return redirect("/quiz")
        
        try:
            int(request.form.get("no"))
        except ValueError:
            session["num"] = 9
            return redirect("/quiz")
        
        session["num"] = int(request.form.get("no")) - 1
        if session["num"] < 1:
            session["num"] = 9
        return redirect("/quiz")
