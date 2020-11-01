from flask import Flask, flash, render_template, request, redirect, session
from cs50 import SQL
from tempfile import mkdtemp
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///maindb.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")

    if not request.form.get("username"):
        flash("Please provide a username")
        return redirect("/login")

    elif not request.form.get("password"):
        flash("Kindly enter a password")
        return redirect("/login")

    rows = db.execute("SELECT * FROM users WHERE username = :username",
                        username=request.form.get("username"))
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        flash("Invalid username and/or password!")
        return redirect("/login")
    session["user_id"] = rows[0]["id"]
    flash("You have successfully logged in.")
    return redirect("/home")



@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if not request.form.get("fname"):
        flash("Enter your name.")
        return redirect("/register")

    if not request.form.get("username"):
        flash("Username field is blank!")
        return redirect("/register")

    elif not request.form.get("password"):
        flash("Password field is blank!")
        return redirect("/register")

    elif request.form.get("password") != request.form.get("confirmpass"):
        flash("Passwords do not match!")
        return redirect("/register")
    else:
        hashpwd = generate_password_hash(request.form.get("password"))
        musrs = db.execute("SELECT * FROM users WHERE username=:username",
                             username=request.form.get("username"))
        if len(musrs) != 0:
            flash("Username not available!")
            return redirect("/register")
        resp = db.execute("INSERT INTO users(fullname, usertype, semester, username, hash, lab1, lab2) VALUES(:fullname, :usertype, :semester,:username, :hash, :lab1, :lab2)", fullname=request.form.get("fname"), usertype="student", semester=request.form.get("semester"), username=request.form.get("username"), hash=hashpwd, lab1=0, lab2=0)
        session["user_id"] = resp
        return redirect("/home")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have successfully logged out.")
    return redirect("/login")


@app.route("/home")
@login_required
def home():
    fname = db.execute("SELECT fullname FROM users WHERE id=:cid", 
                        cid=session["user_id"])[0]["fullname"]
    lab1 = db.execute("SELECT lab1 FROM users WHERE id=:cid", cid=session["user_id"])[0]["lab1"]
    lab2 = db.execute("SELECT lab2 FROM users WHERE id=:cid", cid=session["user_id"])[0]["lab2"]
    return render_template("home.html",fname=fname,lab1=str(lab1),lab2=str(lab2))


@app.route("/expa1", methods = ["GET", "POST"])
@login_required
def expa1():
    if request.method == "GET":
        return render_template("expa1.html")
    else:
        points=0
        ans1 = int(request.form.get("qn1"))
        ans2 = int(request.form.get("qn2"))
        ans3 = int(request.form.get("qn3"))
        ans4 = int(request.form.get("qn4"))
        ans5 = int(request.form.get("qn5"))
        if ans1 == 2:
            points+=2
        if ans2 == 3:
            points+=2
        if ans3 == 4:
            points+=2
        if ans4 == 1:
            points+=2
        if ans5 == 2:
            points+=2
        if points > 6:
            db.execute("UPDATE users SET lab1=:lab1 WHERE id=:cid", lab1=1, cid=session["user_id"])
            flash("You have successfully completed Experiment1 of Mechanical.")
            return redirect("/home")
        else:
            flash("You did not score sufficient points, try again later.")
            return redirect("/home")

@app.route("/expa2")
@login_required
def expa2():
    return render_template("expa2.html")


@app.route("/expb1")
@login_required
def expb1():
    return render_template("expb1.html")


@app.route("/expb2")
@login_required
def expb2():
    return render_template("expb2.html")


if __name__ == '__main__':
    app.run()