import flask
from flask import make_response, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from functools import wraps

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "thissecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

#Defines the User table in the site.db Database file.

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


# app.route "/"
# Starting page that lets you know the Flask app is running

@app.route("/", methods=["GET", "POST"])
def index():
    return jsonify({"Message": "It works"})

# tokenRequired
# Checks to see if the user's token is valid. The SECRET_KEY created at the beginning of the program is used
# to decode the token generated during the login.

def tokenRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")

        if not token:
            return jsonify({"Message": "Token is missing!"})

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            currentUser = User.query.filter_by(public_id=data["public_id"]).first()
        except:
            return jsonify({"Message": "Token is invalid"})

        return f(currentUser, *args, **kwargs)

    return decorated

# app.route /create
# This route allows you to create a username and password that will be entered into the User table in the site.db database.
# A public_id is generated and the password will be stored as a hash using sha256 encryption.

@app.route("/create/<username>/<password>", methods=["GET", "POST"])
def create(username, password):
    

    hashPassword = generate_password_hash(password, method="sha256")
    newUser = User(public_id=str(uuid.uuid4()), name=username, password=hashPassword)
    db.session.add(newUser)
    db.session.commit()

    return jsonify({"Message": "Created"})

#app.route /users
#This route is only accessible by a user that has successfully logged in and has generated a valid token.
#Each token is unique to the user, therefore a token belonging to one user cannot be used to access the users
#page of another.

@app.route("/users/<name>", methods=["GET"])
@tokenRequired
def user(currentUser, name):
    if currentUser.name != name:
        return jsonify({"Message": "Error"})

    return f"Welcome {currentUser.name} to your own page!"

#app.route /login
# This route is used to login using a username and password in the URL. 
# THe route generates a token if the password hash matches the hashed password in the database.
# You can either create your own user in the database using the create route or use
# the username "admin" and the password "pass" to test the login route.

@app.route("/login/<name>/<password>", methods=["GET", "POST"])
def login(name, password):

    user = User.query.filter_by(name=name).first()

    if not user:
        return jsonify({"Message": "Username or password incorrect"})

    if check_password_hash(user.password, password):
        token = jwt.encode(
            {
                "public_id": user.public_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
            },
            app.config["SECRET_KEY"],
        )
        resp = make_response(redirect("/users/" + user.name))
        resp.set_cookie("token", token)
        return resp

    return jsonify({"Message": "Username or password incorrect"})


if __name__ == "__main__":
    app.run(debug=True)
