from flask import Flask, render_template, g
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
    db.row_
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

def dictionarizeData(rows, columnsData):
    results = []
    columns = tuple([column[0] for column in columnsData])
    for row in rows:
        results.append(dict(zip(columns, row)))
    return results


app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()
        g.mysql_cursor.close()


# routes
@app.route("/")
def home():
    return render_template("home.html", title="Home")

@app.route("/answer")
def answer():
    return render_template("answer.html", title="Answer Questions")

@app.route("/ask")
def ask():
    return render_template("ask.html", title="Ask Question")
    
@app.route("/login")
def login():
    return render_template("login.html", title="Login")

@app.route("/question")
def question():
    return render_template("question.html", title="Question")

@app.route("/register")
def register():
    return render_template("register.html", title="Register")

@app.route("/unanswered")
def unanswered():
    return render_template("unanswered.html", title="Unanswered")

@app.route("/users")
def users():
    return render_template("users.html", title="User Setup")



if __name__ == "__main__":
    app.run(debug=True)