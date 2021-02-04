from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, session, url_for, Blueprint
import sqlite3
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask import g

#Setting everything up


app = Flask(__name__, static_url_path='/Users/angelikaanette/Documents/Environments/Static')

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#This function will be used to restrict access to some pages for non-users
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/sign-in")
        return f(*args, **kwargs)
    return decorated_function

#Function that established the connection to the database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#This is the main home page
@app.route('/')
def index():
    return render_template('t4sg_index.html')

#Page to sign up as an user
@app.route('/sign-up', methods=["GET", "POST"])
def register():
#    connect to the database
    db = get_db_connection()
    if request.method == "GET":
        return render_template('t4sg_sign_up.html')


    else:
    # when trying to sign up:
     #getting all the inputs from the forms
       password = request.form.get("password")
       rpassword = request.form.get("rpassword")
       email = request.form.get("email")
       first_name = request.form.get("firstname")
       last_name = request.form.get("lastname")
    # checking if passwords match
       if password != rpassword:
            problems = ['Passwords do not match']
            return render_template('t4sg_sign_up.html', problems=problems)
       else:
            # Hashing the password for security
            hashpassword = generate_password_hash(password)
            # Inserting user data to the database
            db.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?,?,?,?)",
            (first_name, last_name, email, hashpassword))
            db.commit()
            db.close()
            # prompting the user to log in
            return redirect(url_for('signin'))


@app.route('/sign-in', methods=["GET", "POST"])
def signin():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST) so wants to sign in
    if request.method == "POST":
        #connecting with the db
        db = get_db_connection()
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?",
                          (request.form.get("email"),)).fetchall()

        # Ensure username exists and password is correct
        
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
        # send user back to try again and tell what the problem is
            problems = ['Incorrect email and/or password']
            return render_template('t4sg_sign_in.html', problems=problems)
            db.close()
        else:
        #log the user in and remember their unique id
            session["user_id"] = rows[0]["id"]
            return redirect("/home")
            db.close()
    
    # user is trying to access the sign in page with a get request
    else:
        return render_template("t4sg_sign_in.html")
    

@app.route('/home')
@login_required
def home():
    #presenting all created posts
    db = get_db_connection()
    posts = db.execute('SELECT * FROM posts ORDER BY created DESC').fetchall()
    db.close()
    return render_template('t4sg_home.html', posts=posts)

@app.route('/new-post', methods=["GET", "POST"])
@login_required
def new_post():
    # connecting to the database
    db = get_db_connection()
    # showing the page of creating a post
    if request.method == "GET":
        return render_template('t4sg_new_post.html')
    else:
        # getting the input from the page
        title = request.form.get("title")
        content = request.form.get("content")
        # storing the posts in the database
        db.execute("INSERT INTO posts (title, content) VALUES (?,?)",
        (title, content))
        db.commit()
        db.close()
        return redirect("/home")
               
@app.route("/sign-out")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to homepage
    return redirect("/")
    
