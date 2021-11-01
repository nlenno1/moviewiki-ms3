import os
from datetime import datetime
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId  # to render an object id in a bson format
if os.path.exists("env.py"):
    import env


# create an instance of Flask called app
app = Flask(__name__)

# retieving the hidden env variable for use in the app
app.config["MONGO_DB"] = os.environ.get("MONGO_DB")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# create instance of pymongo using contructor with app
mongo = PyMongo(app)


# Functions


def create_single_review():
    review = {
        "reviewer": session['user'],
        "review_title": request.form.get("review-title").lower(),
        "review": request.form.get("movie-review"),
        "review_date": datetime.now(),
        "star_rating": int(request.form.get("star-count"))
    }
    return review


def mongo_prefix_select(collection_name):
    search_prefix = {
        "users": mongo.db.users,
        "movies": mongo.db.movies,
        "genre": mongo.db.genre
    }
    mongo_prefix = search_prefix[collection_name]
    return mongo_prefix


def find_one_with_key(collection_name, search_key, search_value):
    movie = mongo_prefix_select(collection_name).find_one(
        {search_key: search_value})
    return movie


def update_collection_item(collection_name, search_key, search_value,
                           update_operator, key_to_update, new_value):
    mongo_prefix_select(collection_name).update_one(
        {search_key: search_value}, {update_operator:
                                     {key_to_update: new_value}})


def remove_collection_item(collection_name, search_key, search_value):
    mongo_prefix_select(collection_name).delete_one({search_key: search_value})


def add_collection_item(collection_name, search_key, search_value):
    mongo_prefix_select(collection_name).insert_one({search_key: search_value})


# app.route
@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    if len(session) == 0:
        session["user"] = None
    movies = list(mongo.db.movies.find())
    return render_template("home.html", movies=movies)


@app.route("/genre")
def get_all_genre():
    genre_list = list(mongo.db.genre.find())
    return render_template("genre-management.html", genre_list=genre_list)


@app.route("/genre/add", methods=["POST"])
def add_genre():
    new_genre_name = request.form.get('genre-name')
    mongo.db.genre.insert_one({
        "genre_name": new_genre_name.lower()
    })
    flash("Genre " + new_genre_name.title() + " added!")
    return redirect(url_for('get_all_genre'))


@app.route("/genre/delete/<genre_id>")
def delete_genre(genre_id):
    mongo.db.genre.remove({
        "_id": ObjectId(genre_id)
    })
    flash("Genre Deleted")
    return redirect(url_for('get_all_genre'))


@app.route("/genre/update/<genre_name>,<genre_id>", methods=["POST"])
def update_genre(genre_id, genre_name):
    """
    function to update a genre name in the DB
    """
    # store input data in a variable using the genre_name to make up the input
    # name value and removing any spaces
    new_genre_name = request.form.get(genre_name.replace(
                                        " ", "-") + '-replacement-genre-name')
    # updating the informatiion in the DB using the _id to find the documnet
    mongo.db.genre.update({"_id": ObjectId(genre_id)}, {
                                "genre_name": new_genre_name.lower()})
    flash("Genre Updated")
    return redirect(url_for('get_all_genre'))


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
            "favourite-genre": request.form.getlist('favourite-genre').lower()
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
        if request.form.get("image-link"):
            image_link = request.form.get("image-link")
        else:
            image_link = "../static/img/movie-placeholder.png"
        release_date = request.form.get("release-date")
        new_movie = {
            "movie_title": request.form.get("movie-title").lower(),
            "release_date": datetime.strptime(release_date, '%Y-%m-%d'),
            "age_rating": request.form.get("age-rating"),
            "duration": request.form.get("duration"),
            "genre": request.form.getlist("movie-genre"),
            "director": request.form.get("director").lower(),
            "cast_members": request.form.get("cast-members").lower(
                            ).split(","),
            "movie_synopsis": request.form.get("movie-synopsis"),
            "movie_description": request.form.get("movie-description"),
            "image_link": image_link,
            "trailer_link": request.form.get("trailer-link"),
            "reviews": [],
            "latest_reviews": [],
            "created_by": session['user'],
            "is_part_of_series": False,
            "average_rating": 0.0
        }

        if request.form.get("submit-series-info"):
            new_movie["is_part_of_series"] = True
            new_movie["series_position"] = request.form.get(
                                                "series-checkboxes")
            new_movie["series_name"] = request.form.get("series-name").lower()

            if new_movie["series_position"] == "start":
                new_movie["next_movie_title"] = request.form.get(
                                            "next-movie-name").lower()
            elif new_movie["series_position"] == "end":
                new_movie["previous_movie_title"] = request.form.get(
                                                "previous-movie-name").lower()
            else:
                new_movie["previous_movie_title"] = request.form.get(
                                                "previous-movie-name").lower()
                new_movie["next_movie_title"] = request.form.get(
                                            "next-movie-name").lower()

        if request.form.get("submit-movie-review"):
            review = create_single_review()
            new_movie["reviews"].append(review)
            new_movie["latest_reviews"].append(review)
            new_movie["average_rating"] = review["star_rating"]
            mongo.db.users.update_one({"username": session["user"]},
                                      {"$inc": {"reviews_submitted": 1}})

        new_id = mongo.db.movies.insert_one(new_movie).inserted_id

        if request.form.get("seen-movie-checkbox"):
            mongo.db.users.update_one({"username": session["user"]},
                                      {"$push": {"movies_watched": new_id}})

        if request.form.get("write-review-switch"):
            mongo.db.users.update_one({"username": session["user"]},
                                      {"$push": {"movies_reviewed": new_id}})

        time.sleep(3)
        flash("New Movie Added")
        return redirect(url_for("view_movie", movie_id=new_id))

    genre_list = mongo.db.genre.find()
    return render_template("create-movie.html", genre_list=genre_list)


@app.route("/view-movie/<movie_id>")
def view_movie(movie_id):
    movie = mongo.db.movies.find_one(
            {'_id': ObjectId(movie_id)})
    if session["user"] is not None:
        user = mongo.db.users.find_one(
            {"username": session["user"]},
            {"_id": 0, "movies_watched": 1}
        )

        if movie["movie_title"] in user["movies_watched"]:
            user_watched = True
        else:
            user_watched = False
    else:
        user_watched = False

    movie__genre_text_list = ', '.join(name.title() for name in movie["genre"])
    movie["genre"] = movie__genre_text_list
    return render_template("view-movie.html", movie=movie,
                           user_watched=user_watched)


@app.route("/create-review", defaults={'selected_movie_title': None}, methods=["GET", "POST"])
@app.route("/create-review/<selected_movie_title>", methods=["GET", "POST"])
def create_review(selected_movie_title):
    if request.method == "POST":
        requested_movie_name = request.form.get("selected-movie-title").lower()
        movie = mongo.db.movies.find_one({
                                "movie_title": requested_movie_name},
                                 {"_id": 1, "latest_reviews": 1, "reviews": 1})
        if movie:
            new_review = create_single_review()
            mongo.db.movies.update_one({"_id": ObjectId(
                                        movie["_id"])},
                                       {"$push": {"reviews": new_review}})
            # generate an average reviews score
            total_review_score = 0
            # add all the review scores together from the data pulled from
            # the DB
            for review in movie["reviews"]:
                total_review_score += int(review["star_rating"])
            # add the review score just pushed to the DB
            total_review_score += new_review["star_rating"]
            # divide the result by the amount of old scores plus 1 for the
            # score just added
            new_average_review_score = round(total_review_score/(len(
                                            movie["reviews"]) + 1), 2)

            # set the variable in the DB to the new value
            mongo.db.movies.update_one({"_id": ObjectId(
                                        movie["_id"])},
                                       {"$set": {"average_review_score":
                                        new_average_review_score}})

            if len(movie["latest_reviews"]) > 2:
                movie["latest_reviews"].pop()
            movie["latest_reviews"].append(new_review)
            mongo.db.movies.update_one({"_id": ObjectId(
                                    movie["_id"])},
                                    {"$set": {
                                      "latest_reviews": movie
                                      ["latest_reviews"]}})

            return redirect(url_for('view_reviews', movie_id=movie["_id"]))

        else:
            flash(f"There is no movie called '{requested_movie_name.title()}' "
                  f"in the database.\nEither create a profile for this movie "
                  f"or try a different Movie Title")
        return redirect(url_for('create_review'))

    movie_title_list = mongo.db.movies.find({}, {"movie_title": 1})
    return render_template(
        "create-review.html", movie_title_list=movie_title_list,
        selected_movie_title=selected_movie_title)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/view-reviews/<movie_id>")
def view_reviews(movie_id):
    movie = find_one_with_key("movies", "_id", ObjectId(movie_id))
    list(movie)
    return render_template("view-reviews.html", movie=movie)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html")


# application running instructions by retieving hidden env variables
if __name__ == "__main__":
    # retrieve the hidden env values and set them in variables
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)  # this only used in development to debug
