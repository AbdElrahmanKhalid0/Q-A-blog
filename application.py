from flask import Flask, render_template, g, request, redirect, flash, url_for, get_flashed_messages, session
from mysql.connector import connect
from werkzeug.security import generate_password_hash, check_password_hash
import os

# database connection funcitons
def db_connect():
    db = connect(
        username=os.environ.get("DB_USERNAME"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_QABLOG")
    )
    cursor = db.cursor()
    g.mysql_db = db
    g.mysql_cursor = cursor

def get_db():
    if not hasattr(g, 'mysql_db'):
        db_connect()
    return g.mysql_db

def get_db_cursor():
    if not hasattr(g, 'mysql_cursor'):
        db_connect()
    return g.mysql_cursor

def dictionarizeData(data, columnsData, oneRow=False):
    columns = tuple([column[0] for column in columnsData])
    if not oneRow:
        results = []
        for row in data:
            results.append(dict(zip(columns, row)))
        return results
    return dict(zip(columns, data))


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
    db = get_db()
    cursor = get_db_cursor()
    cursor.execute("SELECT * FROM questions Where status='answered'")
    questions = dictionarizeData(cursor.fetchall(), cursor.description)
    return render_template("home.html", title="Home", questions=questions)

@app.route("/answer")
def answer():
    return render_template("answer.html", title="Answer Questions")

@app.route("/ask")
def ask():
    return render_template("ask.html", title="Ask Question")
    
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (request.form.get("username"),))
        user = cursor.fetchone()
        if user:
            user = dictionarizeData(user, cursor.description, True)
            if check_password_hash(user["password"], request.form.get("password")):
                flash("You have logged in successfully!", "success")
                session["username"] = user["username"]
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

@app.route("/question")
def question():
    return render_template("question.html", title="Question")

@app.route("/register", methods=['POST','GET'])
def register():
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
    return render_template("unanswered.html", title="Unanswered")

@app.route("/users")
def users():
    return render_template("users.html", title="User Setup")

@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username", None)
        
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)