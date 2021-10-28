import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId  # to render an object id in a bson format
if os.path.exists("env.py"):
    import env
from datetime import datetime, date


# create an instance of Flask called app
app = Flask(__name__)

# retieving the hidden env variable for use in the app
app.config["MONGO_DB"] = os.environ.get("MONGO_DB")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# create instance of pymongo using contructor with app
mongo = PyMongo(app)


@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    movie_list = mongo.db.movies.find()
    return render_template("home.html", movies=movie_list)


@app.route("/get_all_genre")
def get_all_genre():
    genre_list = mongo.db.genre.find()
    return render_template("genre-management.html", genre_list=genre_list)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        requested_username = request.form.get("username")
        existing_user = mongo.db.users.find_one(
            {"username": requested_username.lower()}
        )

        if existing_user:
            flash("Username " + requested_username.capitalize() +
                  " already exists")
            return redirect(url_for("signup"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "firstname": request.form.get("firstname").lower(),
            "lastname": request.form.get("lastname").lower(),
            "dob": request.form.get("dob"),
            "email": request.form.get('email'),
            "favourite-genre": request.form.getlist('favourite-genre')
        }
        mongo.db.users.insert_one(register)

        # put the user into session and load profile page
        session['user'] = request.form.get("username").lower()
        flash("Registration Successful " + session["user"].capitalize() + "!")
        return redirect(url_for('profile', username=session['user']))

    genre_list = mongo.db.genre.find()
    return render_template("signup.html", genre_list=genre_list)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # check if username is on the BD
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if existing_user:
            if check_password_hash(
              existing_user["password"], request.form.get("password")):
                session['user'] = request.form.get("username").lower()
                flash("Welcome " + session["user"].capitalize())
                return redirect(url_for('profile', username=session['user']))
            else:
                flash("The information entered is incorrect")
                return redirect(url_for('signin'))

        else:
            flash("The information entered is incorrect")
            return redirect(url_for('signin'))

    return render_template("signin.html")


@app.route("/signout")
def signout():
    flash("You have signed out")
    session.pop("user")
    movie_list = mongo.db.movies.find()
    return render_template("home.html", movies=movie_list)


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    user = mongo.db.users.find_one(
            {"username": username},
            {"password": 0}
          )
    return render_template("profile.html", user=user)


@app.route("/create-movie", methods=["GET", "POST"])
def create_movie():
    if request.method == "POST":
        # if movie watch switch is active then add to user profile
        new_movie = {
            "movie_title": request.form.get("movie-title"),
            "release_date": request.form.get("release-date"),
            "age_rating": request.form.get("age-rating"),
            "genre": request.form.getlist("movie-genre"),
            "director": request.form.get("director"),
            "cast_members": request.form.get("cast-members"),
            "movie_synopsis": request.form.get("movie-synopsis"),
            "movie_description": request.form.get("movie-description"),
            "image_link": request.form.get("image-link"),
            "trailer_link": request.form.get("trailer-link"),
            "series_position": request.form.get("series-checkboxes"),
            "series_name": request.form.get("series-name"),
            "previous_movie_title": request.form.get("previous-movie-name"),
            "next_movie_title": request.form.get("next-movie-name"),
            "numb_of_reviews": 0,
            "reviews": [{
                "reviewer": session['user'],
                "review_title": request.form.get("review-title"),
                "review": request.form.get("movie-review"),
                "review_date": datetime.now(),
                "star_rating": request.form.get("star-count")
            }],
            "average_rating": 0,
            "created_by": session['user']
        }
        mongo.db.movies.insert_one(new_movie)
        flash("New Movie Added")
        brand_new_movie = mongo.db.users.find_one(
            {"movie_title": request.form.get("movie-title")})
        return redirect(url_for(
                        "view_movie", movie_id=ObjectId(brand_new_movie)))

    genre_list = mongo.db.genre.find()
    return render_template("create-movie.html", genre_list=genre_list)


@app.route("/create-review", methods=["GET", "POST"])
def create_review():
    movie_title_list = mongo.db.movies.find({}, {"movie_name": 1})
    return render_template(
        "create-review.html", movie_title_list=movie_title_list)


@app.route("/view-movie/<movie_id>")
def view_movie(movie_id):
    movie = mongo.db.movies.find_one(
            {'_id': ObjectId(movie_id)})
    return render_template("view-movie.html", movie=movie)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html")


# application running instructions by retieving hidden env variables
if __name__ == "__main__":
    # retrieve the hidden env values and set them in variables
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)  # this only used in development to debug
