from flask import Blueprint, url_for, jsonify, request
from utils import get_db, get_db_cursor, dictionarizeData
from werkzeug.security import check_password_hash
from datetime import datetime
from functools import wraps

api = Blueprint('api', __name__)
DATE_FORMAT = '%Y-%m-%d'

# def authentication_required(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         if not request.authorization:
#             return jsonify({"error":"Authentication Error"}), 403
        
#         cursor = get_db_cursor()
#         cursor.execute("SELECT * FROM users WHERE username = %s", (request.authorization.username, ))
#         user = cursor.fetchone()
#         if not user or not check_password_hash(user["password"], request.authorization.password):
#             return jsonify({"error":"Authentication Error"}), 403
#         return func(*args, **kwargs)
#     return wrapper


# this didn't work before changing the __name__ of the returned function because in every time the
# decorator wraps a function the endpoint name will be wrapper and that makes all the endpoints
# have the same name and that shouldn't happen

def authentication_required(func):
    def wrapper(*args, **kwargs):
        if not request.authorization:
            return jsonify({"error":"Authentication Error"}), 403
        
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (request.authorization.username, ))
        user = cursor.fetchone()
        if not user or not check_password_hash(user["password"], request.authorization.password):
            return jsonify({"error":"Authentication Error"}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@api.route("/")
def index():
    return f""" <pre>
    Welcome to the Q&A Blog API!

    before using the API you should have an account you can have a one by visiting <a href='{url_for('register')}'>Register</a>
    
    Use an Authorization header to be able to use the API and you should give in it the user data
    in base64 encode so it should be for example in javascript like this:
    <pre><b>'Basic ' + base64.encode(username + ":" + password)</b></pre>
    or
    <pre><b>'Basic ' + btoa(username + ":" + password)</b></pre>

    The following endpoints are available:
    GET /questions
      USAGE:
        Get all the Answered Questions in the follwing format
        
        <b>{'''{
            "answer": The Question Answer,
            "asked": The username of the expert who was asked the question,
            "asker": The username of the person who asked the question,
            "question": The Question body,
            "status": the status of the question which is "answered" in this situation,
            "time": the time when the Question was asked
        }'''}</b>

    GET /questions/:search_query
      USAGE:
        Get all the questions that match with the search query
    GET /asker/:asker_username
      USAGE:
        Get all the questions that its asker is the user with the given username
    GET /asked/:asked_username
      USAGE:
        Get all the questions that the expert who answered it is the user with the given username
    POST /questions
      USAGE:
        Ask a new question with the user information that was given with the Authorization Header.
      PARAMS:
        question - string - the question body
        asked_username - string - the asked expert username
      RETURNS:
        {"{'status':'success'}"} - in case the question was added
 </pre>
  """
    return f"to use this api you should first sign up for an account in this page <a href='{url_for('register')}'>Register</a>"

@api.route("/questions")
@authentication_required
def questions():
    cursor = get_db_cursor(False)
    cursor.execute("SELECT questions.body as question, answers.body as answer,\
                    questions.asker_username as asker, questions.asked_username as asked,\
                    questions.status as status, questions.ask_time as time FROM questions JOIN answers\
                    ON questions.id = answers.question_id WHERE answers.answer_owner = questions.asked_username")
    
    return jsonify({"questions":dictionarizeData(cursor.fetchall(), cursor.description)})

@api.route("/questions/search/<string:query>")
@authentication_required
def questions_search(query):
    cursor = get_db_cursor(False)
    cursor.execute("SELECT questions.body as question, answers.body as answer,\
                    questions.asker_username as asker, questions.asked_username as asked,\
                    questions.status as status, questions.ask_time as time FROM questions JOIN answers\
                    ON questions.id = answers.question_id \
                    WHERE answers.answer_owner = questions.asked_username and body like %s", ("%" + query + "%",))

    return jsonify({"questions":dictionarizeData(cursor.fetchall(), cursor.description)})

@api.route("/questions/asker/<string:username>")
@authentication_required
def questions_asker_user(username):
    cursor = get_db_cursor(False)
    cursor.execute("SELECT * FROM questions WHERE asker_username = %s and status = 'answered'", (username, ))

    return jsonify({"questions":dictionarizeData(cursor.fetchall(), cursor.description)})

@api.route("/questions/asked/<string:username>")
@authentication_required
def questions_asked_user(username):
    cursor = get_db_cursor(False)
    cursor.execute("SELECT * FROM questions WHERE asked_username = %s and status = 'answered'", (username, ))

    return jsonify({"questions":dictionarizeData(cursor.fetchall(), cursor.description)})

@api.route("/questions", methods=["POST"])
@authentication_required
def add_question():
    question = request.get_json()
    question_body = question.get("question")
    question_asker_username = question.get("asker_username")
    question_asked_username = question.get("asked_username")

    db = get_db()
    cursor = get_db_cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (question_asked_username, ))
    asked_user = cursor.fetchone()
    if not asked_user:
        return jsonify({"error":f"there is no expert with the username {request.authorization.username}"})

    cursor.execute("INSERT INTO questions (ask_time, body, asker_username, asked_username) VALUES (%s, %s, %s, %s)",
         (datetime.strftime(datetime.now(),DATE_FORMAT),
          question_body,
          request.authorization.username,
          asked_user["username"]))
    db.commit()

    return jsonify({"status":"success"}), 201