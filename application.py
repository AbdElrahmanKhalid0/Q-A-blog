from flask import Flask, render_template, g, request, redirect, flash, url_for, get_flashed_messages, session, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from utils import get_db, get_db_cursor, dictionarizeData
from datetime import datetime
import os

DATE_FORMAT = '%Y-%m-%d'
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()
        g.mysql_cursor.close()


# routes
@app.route("/")
def home():
    if 'username' not in session:
        return redirect(url_for("login", next="home"))

    cursor = get_db_cursor()
    # in here ordered by the id instead of the date because the date won't be accurate
    # in case that the day has many questions
    cursor.execute("SELECT * FROM questions Where status='answered' ORDER BY id DESC")
    questions = dictionarizeData(cursor.fetchall(), cursor.description)
    return render_template("home.html", title="Home", questions=questions)

@app.route("/answer", methods=['GET','POST'])
def answer():
    if 'username' not in session:
        return redirect(url_for("login", next="answer"))

    if session['role'] != 'expert' and session['role'] != 'admin':
        abort(403)

    cursor = get_db_cursor()
    if request.method == 'POST':
        db = get_db()
        cursor.execute("INSERT INTO answers (body, question_id, answer_owner) VALUES (%s, %s, %s)",
            (request.form.get("answer"), request.args.get("id"), session["username"]))
        cursor.execute("UPDATE questions SET status='answered' WHERE id=%s", (request.args.get("id"),))
        db.commit()
        flash("Your answer was submitted successfully!", "success")
        return redirect(url_for('answer'))
        
    cursor.execute("SELECT * FROM questions WHERE status='not answered' and asked_username=%s",(session["username"],))
    questions = dictionarizeData(cursor.fetchall(), cursor.description)

    return render_template("answer.html", title="Answer Questions", questions=questions)

@app.route("/ask", methods=['GET', 'POST'])
def ask():
    if 'username' not in session:
        return redirect(url_for("login", next="ask"))

    cursor = get_db_cursor()
    # TODO: make the expert not able to ask himself
    if request.method == 'POST':
        db = get_db()
        cursor.execute("INSERT INTO questions (ask_time, body, asker_username, asked_username) VALUES (%s, %s, %s, %s)",
         (datetime.strftime(datetime.now(),DATE_FORMAT),
          request.form.get("answer"),
          session["username"],
          request.form.get("expert")))
        db.commit()
        flash("Your question has been submitted successfully, and soon you will be able to get the answer to it.", "success")
        return redirect(url_for("ask"))

    cursor.execute("SELECT * FROM users Where role='expert'")
    experts = dictionarizeData(cursor.fetchall(), cursor.description)


    return render_template("ask.html", title="Ask Question", experts = experts)
    
@app.route("/login", methods=['GET','POST'])
def login():
    if 'username' in session:
        return redirect(url_for("home"))

    if request.method == 'POST':
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (request.form.get("username"),))
        user = cursor.fetchone()
        if user:
            user = dictionarizeData(user, cursor.description, True)
            if check_password_hash(user["password"], request.form.get("password")):
                flash("You have logged in successfully!", "success")
                session["username"] = user["username"]
                session["role"] = user["role"]
                if request.args:
                    if request.args.get("id"):
                        return redirect(url_for(request.args.get("next"), id=request.args.get("id")))
                    else:
                        return redirect(url_for(request.args.get("next")))
                else:
                    return redirect(url_for("home"))
            else:
                flash("You should check your input!!", "danger")
                # in here I redirected the user to the same page to make the request method
                # GET again instead of POST
                return redirect(url_for("login"))
        else:
            flash("There is no user with this username, maybe you should register first!", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", title="Login")

@app.route("/question/<int:id>")
def question(id):
    # TODO: make the question show the comments from other users in its answered page
    if 'username' not in session:
        return redirect(url_for("login", next="question", id=id))

    cursor = get_db_cursor()
    cursor.execute("SELECT questions.body as question, answers.body as answer,\
                    questions.asker_username as asker, questions.asked_username as asked,\
                    questions.status as status FROM questions JOIN answers\
                    ON questions.id = answers.question_id WHERE questions.id = %s",(id,))
    question = cursor.fetchone()
    if question:
        question = dictionarizeData(question, cursor.description, True)
        return render_template("question.html", title="Question", question=question)
    
    flash("There is no question in here!!", "info")
    return redirect(url_for("home"))

@app.route("/register", methods=['POST','GET'])
def register():
    if 'username' in session:
        return redirect(url_for("home"))

    if request.method == 'POST':
        db = get_db()
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (request.form.get("username"),))
        user = cursor.fetchone()
        if user:
            flash("This username isn't available, Try choosing another one!", "danger")
        else:
            hashed_password = generate_password_hash(request.form.get("password"))
            cursor.execute("INSERT INTO users (username, password) values (%s, %s)", (request.form.get("username"), hashed_password))
            db.commit()
            flash("You signed up successfully, You can login now", "success")
            return redirect(url_for("login"))
    
    return render_template("register.html", title="Register")

@app.route("/unanswered")
def unanswered():
    if 'username' not in session:
        return redirect(url_for("login", next="unanswered"))

    cursor = get_db_cursor()
    cursor.execute("SELECT * FROM questions Where status='not answered'")
    questions = dictionarizeData(cursor.fetchall(), cursor.description)

    return render_template("unanswered.html", title="Unanswered", questions=questions)

@app.route("/unanswered/answer/<int:id>", methods=['GET','POST'])
def answer_unanswered(id):
    if 'username' not in session:
        return redirect(url_for("login", next="answer_unanswered", id=id))
    
    cursor = get_db_cursor()
    cursor.execute("SELECT * FROM questions WHERE id=%s and status='not answered'", (id,))
    question = cursor.fetchone()
    if question:
        question = dictionarizeData(question, cursor.description, True)
    else:
        flash("There is no an unanswered question with this id!", "info")
        return redirect(url_for('unanswered'))

    if request.method == 'POST':
        db = get_db()
        cursor.execute("INSERT INTO answers (body, question_id, answer_owner) VALUES (%s, %s, %s)",
            (request.form.get("answer"), id, session["username"]))
        # if the one who answered the question was the one who the question was led to its
        # status will be changed to 'answered'
        if question["asked_username"] == session["username"]:
            cursor.execute("UPDATE questions SET status='answered' WHERE id=%s", (id,))
            db.commit()
            flash("Your answer was submitted successfully!", "success")
            return redirect(url_for("unanswered"))
        db.commit()
        flash("Your answer has been submitted","success")
        return redirect(url_for('answer_unanswered', id=id))
    else:
        cursor.execute("SELECT answer_owner, body as answer FROM answers WHERE question_id = %s", (id,))
        answers = cursor.fetchall()
        if answers:
            answers = dictionarizeData(answers, cursor.description)
        print(answers)
        return render_template("answer_unanswered.html", question=question, answers=enumerate(answers) if answers else None)



@app.route("/users", methods=['GET','POST'])
def users():
    if session['role'] != 'admin':
        abort(403)

    cursor = get_db_cursor()
    if request.method == 'POST':
        db = get_db()
        username = request.json["username"]
        role = request.json["role"]
        cursor.execute("UPDATE users SET role=%s WHERE username=%s", (role, username))
        db.commit()
        
        return jsonify({'success':'true'})

    cursor.execute("SELECT * FROM users")    
    users = dictionarizeData(cursor.fetchall(), cursor.description)

    return render_template("users.html", title="User Setup", users=users)

@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username", None)
        session.pop("role", None)
        
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)