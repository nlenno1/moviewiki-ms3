import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId  # to render an object id in a bson format
if os.path.exists("env.py"):
    import env
    from werkzeug.security import generate_password_hash, check_password_hash


# create an instance of Flask called app
app = Flask(__name__)

# retieving the hidden env variable for use in the app
app.config["MONGO_DB"] = os.environ.get("MONGO_DB")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# create instance of pymongo using contructor with app
mongo = PyMongo(app)


@app.route("/")
@app.route("/get_all_genre")
def get_all_genre():
    genre_list = mongo.db.genre.find()
    return render_template("genre-management.html", genre_list=genre_list)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    genre_list = mongo.db.genre.find()
    return render_template("signup.html", genre_list=genre_list)


@app.route("/signin")
def signin():
    return render_template("signin.html")


# application running instructions by retieving hidden env variables
if __name__ == "__main__":
    # retrieve the hidden env values and set them in variables
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)  # this only used in development to debug
