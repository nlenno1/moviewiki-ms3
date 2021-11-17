import os
from datetime import datetime
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


# ---------- Functions ----------
def is_admin():
    """
    calls to db using session id variable to confirm if user is admin
    """
    if session and len(session) > 1 and session["id"]:
        user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                       {"is_superuser": 1})
        if user and user["is_superuser"] is True:
            session["is_superuser"] = True
            return True
    session["is_superuser"] = False
    return False


def is_correct_user(user_id_to_check):
    """
    check if user created document and is allowed to edit by passing in
    created_by variable and calling to db using session id
    """
    if session and len(session) > 1 and session["id"]:
        user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                       {"is_superuser": 1})
        if user and (user["_id"] == ObjectId(user_id_to_check) or session[
                        "is_superuser"] is True):
            return True
    return False


def is_signed_in():
    """
    checks session id against the database to see if the user exists
    """
    if session and len(session) > 1 and session["id"]:
        user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                       {"_id": 1})
        if user:
            return True
    return False


def create_single_review(movie, movie_id=None):
    """
    create review dictionary
    """
    review = {
        "reviewer": session['user'],
        "reviewer_id": session["id"],
        "review_title": request.form.get("review-title").lower(),
        "review": request.form.get("movie-review"),
        "review_date": datetime.now(),
        "star_rating": int(request.form.get("star-count")),
        "review_for": movie["movie_title"],
        "review_for_id": movie["_id"]
    }
    # set movie_id conditional as when creating movie it
    # doesn't have a MongoDB _id yet
    if movie_id is None:
        review["review_for_id"] = movie["_id"]
    else:
        review["review_for_id"] = movie_id
    return review


def mongo_prefix_select(collection_name):
    """
    prefix Switch statement for the functions below
    """
    search_prefix = {
        "users": mongo.db.users,
        "movies": mongo.db.movies,
        "genre": mongo.db.genre
    }
    mongo_prefix = search_prefix[collection_name]
    return mongo_prefix


def find_one_with_id(collection_name, search_id):
    """
    call to the database to return a whole document
    """
    document = mongo_prefix_select(collection_name).find_one(
        {"_id": search_id})
    return document


def find_user():
    """
    call to the database to return users document without password hash
    """
    document = mongo_prefix_select("users").find_one(
               {"_id": ObjectId(session["id"])}, {"password_hash": 0})
    return document


def update_collection_item_dict(collection_name, search_key, search_value,
                                update_operator, array_to_update,
                                array_search_key, array_search_value):
    """
    updates a dictionary in an array field in a document
    """
    mongo_prefix_select(collection_name).update_one(
        {search_key: search_value},
        {update_operator: {array_to_update:
                           {array_search_key: array_search_value}}})


def update_collection_item(collection_name, search_key, search_value,
                           update_operator, new_key, new_value):
    """
    updates a field document
    """
    mongo_prefix_select(collection_name).update_one(
        {search_key: search_value},
        {update_operator: {new_key: new_value}})


def update_average_rating(movie_id, movie=None):
    """
    set movie average_rating variable as average of all review
    ratings for a specified movie
    """
    if movie is None:
        movie = find_one_with_id("movies", movie_id)
    total_review_score = 0
    if len(movie["reviews"]) > 0:
        for review in movie["reviews"]:
            total_review_score += int(review["star_rating"])
        new_average_rating = round(total_review_score/(len(
                                        movie["reviews"])), 2)
    else:
        new_average_rating = 0.0
    update_collection_item("movies", "_id", ObjectId(movie["_id"]),
                           "$set", "average_rating", new_average_rating)


def create_new_latest_reviews(review_list, new_review_dict,
                              to_compare_1, to_compare_2):
    """
    adds new review to the latest review dict and removes the
    oldest if the dict length is over 3
    """
    new_review_list = [review for review in review_list if
                       review[to_compare_1] != to_compare_2]

    if len(new_review_list) > 2:
        new_review_list = new_review_list[0:2]
    new_review_list.append(new_review_dict)
    return new_review_list


def add_review_to_latest_reviews_dicts(movie, new_review_dict):
    """
    update latest review arrays in movie and user document
    """
    user = find_one_with_id("users", ObjectId(session["id"]))
    user["user_latest_reviews"] = create_new_latest_reviews(
        user["user_latest_reviews"], new_review_dict, "review_for_id",
        movie["_id"])
    movie["latest_reviews"] = create_new_latest_reviews(
        movie["latest_reviews"], new_review_dict, "reviewer_id", session["id"])

    update_collection_item("users", '_id', ObjectId(session['id']), "$set",
                           "user_latest_reviews", user["user_latest_reviews"])
    update_collection_item("movies", '_id', ObjectId(movie['_id']), "$set",
                           "latest_reviews", movie["latest_reviews"])


def create_similar_movies_list(collection, collection_list_name, user_list,
                               sort_list_by_key=None, new_list_length=None,
                               movie_id=None, dob=None,
                               movies_watched_list=None):
    """
    creates similar or suggested movies lists
    """
    storage_list = []
    for item in collection:
        if item["_id"] != movie_id:
            if set(user_list).intersection(item[collection_list_name]):
                storage_list.append(item)
    if sort_list_by_key is not None:
        storage_list = sorted(storage_list, key=lambda d: d[sort_list_by_key])
    if dob:
        storage_list = filter_movies_using_age_ratings(storage_list, dob)
    if movies_watched_list:
        storage_list = check_if_user_has_watched(
                        storage_list, movies_watched_list)
    if new_list_length:
        storage_list = storage_list[:new_list_length]
    return storage_list


def find_review_for_movies_in_reviews_list(review_list, reviewer_id):
    """
    find all reviews by one user in a list
    """
    movie_review = []
    if len(review_list) > 0:
        movie_review = [review for review in review_list
                        if review["reviewer_id"] == reviewer_id]
    if len(movie_review) > 0:
        return movie_review[0]


def generate_new_movie_dict(movie_id=None, update=None):
    """
    create new movie dict for add or edit movie
    """
    new_movie = {
        "movie_title": request.form.get("movie-title").lower(),
        "release_date": datetime.strptime(request.form.get(
                                        "release-date"), '%Y-%m-%d'),
        "age_rating": request.form.get("age-rating"),
        "duration": request.form.get("duration"),
        "genre": request.form.getlist("movie-genre"),
        "director": request.form.get("director").lower(),
        "cast_members": request.form.get(
            "cast-members").lower().split(","),
        "movie_synopsis": request.form.get("movie-synopsis"),
        "movie_description": request.form.get("movie-description"),
        "image_link": request.form.get("image-link"),
    }
    if update is None:
        new_movie["reviews"] = []
        new_movie["latest_reviews"] = []
        new_movie["created_by"] = session['id']
        new_movie["is_part_of_series"] = False
        new_movie["average_rating"] = 0.0
    add_series_information_to_dict(new_movie)
    if movie_id and request.form.get("submit-movie-review"):
        review = create_single_review(new_movie, movie_id)
        new_movie["reviews"].append(review)
    return new_movie


def add_series_information_to_dict(new_movie):
    """
    add series info to movie dict
    """
    if request.form.get("submit-series-info"):
        new_movie["is_part_of_series"] = True
    else:
        new_movie["is_part_of_series"] = False

    new_movie["movie_series_info"] = {
        "series_name": request.form.get("series-name").lower(),
        "series_position": request.form.get("series-checkboxes"),
        "previous_movie_title": request.form.get(
                               "previous-movie-name").lower(),
        "next_movie_title": request.form.get("next-movie-name").lower(),
    }


def create_and_add_mini_movie_dict(movie_id, array_name, movie=None):
    """
    create mini movie dict and add to session user profile
    """
    if movie is None:
        movie = find_one_with_id("movies", ObjectId(movie_id))

    new_mini_movie_dict = {
        "movie_id": movie["_id"],
        "movie_title": movie["movie_title"],
        "release_year": movie["release_date"].strftime('%Y')
    }

    update_collection_item("users", "_id", ObjectId(session["id"]), "$push",
                           array_name, new_mini_movie_dict)


def filter_movies_using_age_ratings(movie_list, user_dob):
    """
    create new array with only movies that the user is old enough to watch
    any movie age rating less than 12a, 12, 15 and 18 will be added to the list
    """
    user_age = (datetime.now() - datetime.strptime(  # calculate user age
                            user_dob, '%Y-%m-%d')).days
    storage_list = []
    for movie in movie_list:
        # check first character of age rating
        if movie["age_rating"][0] == "1":
            # convert age rating year number into days
            age_rating_in_days = float(movie["age_rating"].replace(
                                        "a", "")) * float(365.25)
            if age_rating_in_days < user_age:
                storage_list.append(movie)
        else:
            storage_list.append(movie)
    return storage_list


def check_if_user_has_watched(movies_list, watched_list):
    """
    check if a movie id, from a list of movies,
    is not in the user's movies watched list
    """
    storage_list = [movie for movie in movies_list if movie["_id"] not in
                    [movie["movie_id"] for movie in watched_list]]
    return storage_list


def check_key_in_array_of_dicts(array_to_check, key, value_to_check_against):
    for item in array_to_check:
        if value_to_check_against == item[key]:
            return True
    return False


# ---------- app.route ----------
@app.route("/")
@app.route("/home")
def home():
    """
    find all movies, sort them into appropriate lists and
    display on the home screen
    """
    movies = list(mongo.db.movies.find({}, {"movie_title": 1,
                                            "average_rating": 1,
                                            "release_date": 1,
                                            "genre": 1,
                                            "image_link": 1,
                                            "age_rating": 1}).sort(
                                                                "movie_title"))
    # sorted alphabeticallly by title with max of 15
    all_movies = movies[:15]
    # sorted by average rating by title with max of 15
    highest_rated = sorted(movies, key=lambda d: d['average_rating'],
                           reverse=True)[:15]
    # sorted by release date by title with max of 15
    latest_releases = sorted(movies, key=lambda d: d['release_date'],
                             reverse=True)[:15]
    movies_for_you = []  # initialize empty lists
    want_to_watch = []
    if is_signed_in():
        user = find_user()
        if user:  # create list specific to the users
            movies_for_you = create_similar_movies_list(
                            movies, "genre", user["favourite_genres"],
                            'average_rating', 15, None, user["dob"],
                            user["movies_watched"])
            want_to_watch = [movie for movie in movies if movie["_id"] in
                             [movie["movie_id"] for movie in
                              user["movies_to_watch"]]]
            want_to_watch = sorted(want_to_watch, key=lambda d: d[
                                    'average_rating'])[:15]
    return render_template("home.html", all_movies=all_movies,
                           highest_rated=highest_rated,
                           latest_releases=latest_releases,
                           movies_for_you=movies_for_you,
                           want_to_watch=want_to_watch)


@app.route("/search", methods=["POST"])
def movie_title_search():
    """
    search for movies and display results
    """
    query = request.form.get("movie_title_search")
    searched_movies = list(mongo.db.movies.find(
                            {"$text": {"$search": query}}).sort("movie_title"))
    return render_template("movie-search.html", movies=searched_movies)


# genre management
@app.route("/genre")
def get_all_genre():
    """
    view genre management page with genres sorted alphabetically
    """
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))
    genre_list = list(mongo.db.genre.find().sort("genre_name"))
    return render_template("genre-management.html", genre_list=genre_list)


@app.route("/genre/add", methods=["POST"])
def add_genre():
    """
    if new genre name is unique, add it to the DB
    """
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))
    new_genre_name = request.form.get('genre-name').lower()
    # check if genre name already exists
    existing_name = mongo.db.genre.find_one({"genre_name": new_genre_name})
    if existing_name:
        flash("There is a Genre with this name already")
        return redirect(url_for('get_all_genre'))
    mongo.db.genre.insert_one({
        "genre_name": new_genre_name.lower()
    })
    flash("Genre " + new_genre_name.title() + " added!")
    return redirect(url_for('get_all_genre'))


@app.route("/genre/<genre_id>/update", methods=["POST"])
def update_genre(genre_id):
    """
    check for unique name and update a genre name in the DB
    """
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))
    new_genre_name = request.form.get("replacement-genre-name")
    existing_name = mongo.db.genre.find_one({"genre_name": new_genre_name})
    if existing_name:
        flash(f"There is a Genre with the name {new_genre_name} already")
        return redirect(url_for('get_all_genre'))
    genre = mongo.db.genre.find_one({'_id': ObjectId(genre_id)})
    if genre:
        mongo.db.genre.update_one({"_id": ObjectId(genre_id)},
                                  {"$set":
                                  {"genre_name": new_genre_name.lower()}})
        flash(f"Genre Name Updated to {new_genre_name}")
    else:
        flash(f"Unable to Update. Genre {new_genre_name} Not Found")
    return redirect(url_for('get_all_genre'))


@app.route("/genre/<genre_id>/delete")
def delete_genre(genre_id):
    """
    find and delete a selected genre
    """
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))
    genre = find_one_with_id("genre", ObjectId(genre_id))
    if genre:
        mongo.db.genre.delete_one({"_id": genre["_id"]})
        flash(f"Genre {genre['genre_name']} Deleted")
    else:
        flash("No Genre was found so nothing was deleted")
    return redirect(url_for('get_all_genre'))


# user account
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    GET - render sign up form and pass genres for the dropdown select
    POST - if username is unique, add to database and put user into session
    """
    if request.method == "POST":
        requested_username = request.form.get("username")
        existing_user = mongo.db.users.find_one(  # unique username check
            {"username": requested_username.lower()}
        )
        if existing_user:  # if the username is not unique
            flash("Username " + requested_username.capitalize() +
                  " already exists")
            return redirect(url_for("signup"))
        register = {  # create new user dictionary
            "username": request.form.get("username").lower(),
            "password_hash": generate_password_hash(
                              request.form.get("password")),
            "firstname": request.form.get("firstname").lower(),
            "lastname": request.form.get("lastname").lower(),
            "dob": request.form.get("dob"),
            "email": request.form.get('email'),
            "favourite_genres": request.form.getlist('favourite-genre'),
            "date_joined":  datetime.now(),
            "is_superuser": False,
            "movies_reviewed": [],  # unfilled fields
            "movies_watched": [],
            "movies_to_watch": [],
            "user_latest_reviews": [],
        }  # insert dict into DB
        new_id = mongo.db.users.insert_one(register).inserted_id
        session["id"] = str(new_id)  # put the user in session
        session["user"] = register['username']
        is_admin()  # assign is_superuser value
        flash("Registration Successful!")
        return redirect(url_for('profile'))
    genre_list = list(mongo.db.genre.find().sort("genre_name"))
    return render_template("signup.html", genre_list=genre_list)


@app.route("/profile")
def profile():
    """
    display user profile with all the movie lists required
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("Please sign in to access a User Profile")
        return redirect(url_for("signin"))
    user = find_user()
    movies = list(mongo.db.movies.find({}, {"movie_title": 1,
                                            "image_link": 1,
                                            "genre": 1,
                                            "average_rating": 1,
                                            "age_rating": 1}))
    suggested_movies = create_similar_movies_list(  # generate movie lists
                        movies, "genre", user["favourite_genres"],
                        'average_rating', 15, None, user["dob"],
                        user["movies_watched"])
    user_latest_reviews = sorted(user["user_latest_reviews"],
                                 key=lambda d: d['review_date'],
                                 reverse=True)
    movies_to_watch = sorted(user["movies_to_watch"],
                             key=lambda d: d['movie_title'])
    movies_watched = sorted(user["movies_watched"],
                            key=lambda d: d['movie_title'])
    movies_reviewed = sorted(user["movies_reviewed"],
                             key=lambda d: d['movie_title'])
    return render_template("profile.html", user=user,
                           suggested_movies=suggested_movies,
                           user_latest_reviews=user_latest_reviews,
                           movies_to_watch=movies_to_watch,
                           movies_watched=movies_watched,
                           movies_reviewed=movies_reviewed)


@app.route("/profile/reviews/view")
def view_all_user_reviews():
    """
    Find and display all reviews by user
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("Please sign in to access a User Profile")
        return redirect(url_for("signin"))
    movies = mongo.db.movies.find({}, {"reviews": 1})
    user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                   {"username": 1})
    if user:
        reviews = []
        for movie in movies:
            for review in movie["reviews"]:
                if review["reviewer_id"] == str(user["_id"]):
                    reviews.append(review)
        reviews = sorted(reviews, key=lambda d: d[
                                    'review_for'])
        return render_template("view-all-user-reviews.html",
                               reviews=reviews, username=user["username"])
    flash("No User found")
    return render_template("home")


@app.route("/profile/edit", methods=["GET", "POST"])
def edit_user_profile():
    """
    GET - retrive user information and genre and bind it to the form
    POST - if unique username then create dict and update profile
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("Please sign in to access a User Profile")
        return redirect(url_for("signin"))
    if request.method == "POST":
        user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                       {"username": 1})
        requested_username = request.form.get("username").lower()
        existing_user = mongo.db.users.find_one(  # check if username is in use
                        {"username": requested_username.lower()},
                        {"username": 1})
        if existing_user and requested_username != user["username"]:
            flash(f"Sorry, the username {requested_username.title()} \
                    is unavailable")
            return redirect(url_for("edit_user_profile",
                                    user_id=session['id']))
        updated_profile_dict = {
            "username": request.form.get("username").lower(),
            "firstname": request.form.get("firstname").lower(),
            "lastname": request.form.get("lastname").lower(),
            "dob": request.form.get("dob"),
            "email": request.form.get('email'),
            "favourite_genres": request.form.getlist('movie-genre')
        }  # update user document
        mongo.db.users.update_one({"_id": user['_id']},
                                  {"$set": updated_profile_dict})
        flash(f"Updated {updated_profile_dict['username'].capitalize()} \
                Account!")
        return redirect(url_for('profile'))
    user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                   {"dob": 1, "favourite_genres": 1,
                                   "username": 1, "email": 1, "firstname": 1,
                                    "lastname": 1})
    genre_list = list(mongo.db.genre.find().sort("genre_name"))
    for genre in genre_list:  # check user favourite genre for dropdown
        if genre["genre_name"].lower() in user["favourite_genres"]:
            genre["checked"] = True
    return render_template("edit-user-profile.html", genre_list=genre_list,
                           user=user)


@app.route("/profile/<user_id>/delete")
def delete_user_profile(user_id):
    """
    check user account exists and delete
    user_id passed in from edit profile db call
    """
    is_user_allowed = is_correct_user(user_id)
    if not is_user_allowed:
        flash("You do not have the required permissions to delete this"
              " profile")
        return redirect(url_for("home"))
    user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                   {"username": 1})
    if user:  # check if user account exists
        username = user["username"].title()
        mongo.db.users.remove({"_id": ObjectId(user_id)})
        session.clear()
        flash(f"User Profile {username} Deleted")
        return redirect(url_for('home'))
    else:
        flash("No User account was found to delete")
    return redirect(url_for('profile'))


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """
    GET - returns sign in page
    POST - check if user exists, check password hash and if correct
    """
    if request.method == "POST":  # check if username is on the BD
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()},
            {"password_hash": 1, "username": 1}
        )
        if existing_user:  # check password hash
            if check_password_hash(existing_user["password_hash"],
                                   request.form.get("password")):
                session["id"] = str(existing_user["_id"])
                session["user"] = existing_user['username']
                is_admin()  # set is_superuser variable
                flash(f"Welcome Back {existing_user['username'].capitalize()}")
                return redirect(url_for('profile'))
            else:
                flash("The information entered is incorrect")
                return redirect(url_for('signin'))
        else:
            flash("The information entered is incorrect")
            return redirect(url_for('signin'))
    return render_template("signin.html")


@app.route("/signout")
def signout():
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be Signed In to Sign Out")
        return redirect(url_for("signin"))
    flash("You have signed out")
    session.clear()
    return redirect(url_for('home'))


# movie management
@app.route("/movie/add", methods=["GET", "POST"])
def create_movie():
    """
    GET - find and sort genre and age rating lists for movie add form
    POST - if no similar movies titles, generate new movie dict and insert
    into DB. If added, insert review after.
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to add a movie")
        return redirect(url_for("signin"))
    if request.method == "POST":
        new_movie = generate_new_movie_dict()
        existing_movies = mongo.db.movies.find(
                        {"movie_title": new_movie["movie_title"]},
                        {"release_date": 1, "movie_title": 1})
        if existing_movies:
            for movie in existing_movies:
                # convert datetime to string to compare
                if movie["release_date"].strftime(
                     '%Y') == new_movie["release_date"].strftime('%Y'):
                    flash(f"There is already a movie called "
                          f"{new_movie['movie_title'].title()} which was "
                          f"released in "
                          f"{new_movie['release_date'].strftime('%Y')}")
                    flash("Either use the existing movie profile or change"
                          " the release year")
                    return redirect(url_for('view_all_movies'))
        # movie dict insert and returns new ObjectId
        new_id = mongo.db.movies.insert_one(new_movie).inserted_id
        movie = find_one_with_id("movies", ObjectId(new_id))
        if movie:  # check movie was created and add review
            flash(f"Movie {movie['movie_title'].title()} Created")
            if request.form.get("submit-movie-review"):
                new_review = create_single_review(movie)
                mongo.db.movies.update_one({"_id": ObjectId(movie["_id"])},
                                           {"$push": {"reviews": new_review}})
                create_and_add_mini_movie_dict(new_id, "movies_reviewed",
                                               movie)
                add_review_to_latest_reviews_dicts(
                    movie, create_single_review(movie, movie["_id"]))
                update_average_rating(ObjectId(new_id))
                flash("with your Review Added")
            return redirect(url_for("view_movie", movie_id=new_id))
        else:
            flash("An error occured and the Movie was not created")
        return redirect(url_for("create_movie"))
    genre_list = list(mongo.db.genre.find().sort("genre_name"))
    age_ratings = mongo.db.age_ratings.find().sort("uk_rating_order")
    return render_template("create-movie.html", genre_list=genre_list,
                           age_ratings=age_ratings)


@app.route("/movie/<movie_id>/view")
def view_movie(movie_id):
    """
    check movie exists, find user interactions with movie if signed in,
    create required lists and display
    """
    movie = mongo.db.movies.find_one(
            {'_id': ObjectId(movie_id)})
    user_want_to_watch = False
    user_watched = False
    user_reviewed = False
    if is_signed_in():  # check for user documnet
        user = mongo.db.users.find_one(
            {"_id": ObjectId(session["id"])},
            {"_id": 0, "movies_watched": 1, "movies_to_watch": 1,
                "movies_reviewed": 1})
        if user:  # create user account lists
            user_reviewed = check_key_in_array_of_dicts(
                              user["movies_reviewed"],
                              "movie_id", movie["_id"])
            user_watched = check_key_in_array_of_dicts(
                            user["movies_watched"],
                            "movie_id", movie["_id"])
            user_want_to_watch = check_key_in_array_of_dicts(
                                  user["movies_to_watch"],
                                  "movie_id", movie["_id"])
    # create render_template required arguements
    movies = list(mongo.db.movies.find({}, {"genre": 1, "average_rating": 1,
                                            "movie_title": 1,
                                            "release_date": 1,
                                            "latest_reviews": 1,
                                            "image_link": 1}))
    sim_movies = create_similar_movies_list(movies, "genre", movie["genre"],
                                            'average_rating', 15, movie["_id"])
    movie_genre_text_list = ', '.join(name.title() for name in movie["genre"])
    movie["genre"] = movie_genre_text_list  # convert genre list to a string
    latest_reviews = sorted(movie["latest_reviews"], key=lambda d: d[
                        'review_date'], reverse=True)
    return render_template("view-movie.html", movie=movie,
                           user_watched=user_watched,
                           user_want_to_watch=user_want_to_watch,
                           similar_movies=sim_movies,
                           latest_reviews=latest_reviews,
                           user_reviewed=user_reviewed)


@app.route("/movie/<movie_id>/edit", methods=["GET", "POST"])
def edit_movie(movie_id):
    """
    GET - gather data and create lists/variables for display in inputs
    POST - check for movie, create new movie dict, update movie then add
    review to movie and user documnets
    """
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
    if movie:  # use movie["created_by"] id to check if user created movie
        is_user_allowed = is_correct_user(movie["created_by"])
        if not is_user_allowed:
            return redirect(url_for("home"))
        if request.method == "POST":
            updated_movie = generate_new_movie_dict(movie_id, "update")
            mongo.db.movies.update_one({"_id": ObjectId(movie_id)},
                                       {"$set": updated_movie})

            if request.form.get("submit-movie-review"):
                create_and_add_mini_movie_dict(movie_id, "movies_reviewed",
                                               movie)
                add_review_to_latest_reviews_dicts(
                    movie, create_single_review(movie, movie["_id"]))
                update_average_rating(ObjectId(movie_id))

            flash("Movie Profile Successfully Updated")
            return redirect(url_for("view_movie", movie_id=movie_id))
        genre_list = list(mongo.db.genre.find().sort("genre_name"))
        for genre in genre_list:
            if genre["genre_name"].lower() in movie["genre"]:
                genre["checked"] = True
        age_ratings = mongo.db.age_ratings.find().sort("uk_rating_order")
        matching_ids = [review["reviewer_id"] for review in movie["reviews"]
                        if review["reviewer_id"] == session["id"]]
        user_has_reviewed = True if matching_ids else False
        cast_members_string = ','.join(name.title() for name in movie[
                                "cast_members"])
        return render_template("edit-movie.html", genre_list=genre_list,
                               movie=movie, age_ratings=age_ratings,
                               cast_members_string=cast_members_string,
                               user_has_reviewed=user_has_reviewed)
    else:
        flash("Movie Not Found")
        return redirect(url_for('home'))


@app.route("/movie/<movie_id>/delete")
def delete_movie(movie_id):
    """
    check movie exists, if user allowed, delete from all storage locations
    """
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                     {"created_by": 1})
    if movie:
        # compare movie["created_by"] id to check if user created movie
        is_user_allowed = is_correct_user(movie["created_by"])
        if not is_user_allowed:
            flash("You are not allowed to delete this movie")
            return redirect(url_for("home"))
        # remove movie from all users movies_reviewed, watched
        # and to watch arrays
        mongo.db.users.update_many({}, {"$pull": {"movies_reviewed":
                                        {"movie_id": movie["_id"]}}})
        mongo.db.users.update_many({}, {"$pull": {"movies_watched":
                                        {"movie_id": movie["_id"]}}})
        mongo.db.users.update_many({}, {"$pull": {"movies_to_watch":
                                        {"movie_id": movie["_id"]}}})
        # remove movie from all users latest_reviews array
        mongo.db.users.update_many({}, {"$pull": {"user_latest_reviews":
                                        {"review_for_id": movie["_id"]}}})
        mongo.db.movies.delete_one({"_id": movie["_id"]})
        flash("Movie Deleted")
    else:
        flash("Movie Not Found So Not Deleted")
    return redirect(url_for('home'))


# review management
@app.route("/movies/<movie_id>/reviews")
def view_reviews(movie_id):
    """
    view all reviews from a specific movie
    """
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                     {"reviews": 1, "movie_title": 1,
                                     "average_rating": 1})
    movie_reviews = sorted(movie["reviews"], key=lambda d: d[
                                'review_date'], reverse=True)
    return render_template("view-reviews.html", movie=movie,
                           movie_reviews=movie_reviews)


# use movie_if for this app.route not movie_title - request args **!
@app.route("/review/add", methods=["GET", "POST"])
def create_review():
    """
    GET - if args and if no previous reviews pass movie to page and
    create movie title list for display in create review form
    POST - check movie exists, check for previous reviews, create review dict
    and add to movie and user lists
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to add a review")
        return redirect(url_for("signin"))
    if request.method == "POST":
        movie_id = request.form.get('selected-movie-id')
        if movie_id:
            movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                             {"latest_reviews": 1,
                                              "reviews": 1,
                                              "movie_title": 1,
                                              "release_date": 1})
            if movie:  # check for previous review from user
                user = find_one_with_id("users", ObjectId(session["id"]))
                if user:
                    for review in movie["reviews"]:
                        if review["reviewer_id"] == str(user["_id"]):
                            flash("You have already created a review "
                                  "for this movie")
                            return redirect(url_for('edit_review',
                                            movie_id=movie["_id"],
                                            user_id=session["id"]))
                    new_review = create_single_review(movie)
                    mongo.db.movies.update_one({"_id": ObjectId(
                                                movie["_id"])},
                                               {"$push": {
                                                "reviews": new_review}})
                    create_and_add_mini_movie_dict(movie_id, "movies_reviewed",
                                                   movie)
                    update_average_rating(ObjectId(movie["_id"]))
                    add_review_to_latest_reviews_dicts(movie, new_review)
                else:
                    flash("No User was found so your review was not submitted")
                return redirect(url_for('view_reviews', movie_id=movie["_id"]))
            else:
                flash("Movie Not Found")
        else:
            flash("Please select a Movie")
        return redirect(url_for('create_review'))
    movie_id = request.args.get("movie_id")
    if movie_id:
        movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                         {"reviews": 1})
        if movie:  # check for previous review from user
            if len(movie["reviews"]) > 0:
                for review in movie["reviews"]:
                    if review["reviewer_id"] == session["id"]:
                        flash("You have already created a review "
                              "for this movie")
                        return redirect(url_for('edit_review',
                                        movie_id=movie["_id"],
                                        user_id=session["id"]))
    else:
        movie_id = None
    movie_title_list = mongo.db.movies.find(
                        {}, {"movie_title": 1,
                             "release_date": 1}).sort("movie_title")
    return render_template(
        "create-review.html", movie_title_list=movie_title_list,
        selected_movie_id=movie_id)


@app.route("/movie/<movie_id>/review/edit", methods=["GET", "POST"])
def edit_review(movie_id):
    """
    GET - find user review in movie dict and bind to form for editing
    POST - delete old review, create new review dict and push to doc and lists
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        return redirect(url_for('view_reviews', movie_id=movie_id))
    if request.method == "POST":  # check movie exists
        movie = find_one_with_id("movies", ObjectId(movie_id))
        if movie:  # delete old dict create new dict and push to lists & doc
            updated_review = create_single_review(movie)
            update_collection_item_dict("movies", "_id", ObjectId(movie_id),
                                        "$pull", "reviews", "reviewer_id",
                                        session["id"])
            mongo.db.movies.update_one({"_id": ObjectId(movie_id)},
                                       {"$push": {"reviews": updated_review}})
            add_review_to_latest_reviews_dicts(movie, updated_review)
            update_average_rating(ObjectId(movie["_id"]))
            return redirect(url_for('view_reviews', movie_id=movie_id))
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                     {"reviews": 1})
    review = find_review_for_movies_in_reviews_list(
                movie["reviews"], session["id"])
    if review:  # check if user's movie review exists
        return render_template("edit-review.html", movie=movie, review=review)
    else:
        return redirect(url_for('view_reviews', movie_id=movie_id))


@app.route("/movie/<movie_id>/review/delete")
def delete_review(movie_id):
    """
    check movie and review exists, delete from all lists and movie doc
    """
    user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                   {"_id": 1})
    movie = find_one_with_id("movies", ObjectId(movie_id))
    review = find_review_for_movies_in_reviews_list(
                movie["reviews"], str(user["_id"]))
    if review:
        is_user_allowed = is_correct_user(review["reviewer_id"])
        if not is_user_allowed:
            flash("You are not allowed to delete this review")
            return redirect(url_for('view_reviews', movie_id=movie_id))
        # remove review from movie profile reviews list using review_date
        update_collection_item_dict("movies", "_id", ObjectId(movie_id),
                                    "$pull", "reviews",
                                    "review_date",
                                    review["review_date"])
        # remove review from movie profile latest reviews list with review_date
        update_collection_item_dict("movies", "_id", ObjectId(movie_id),
                                    "$pull", "latest_reviews", "review_date",
                                    review["review_date"])
        # remove review from user profile reviews list
        update_collection_item_dict("users", "_id", user["_id"],
                                    "$pull", "movies_reviewed",
                                    "movie_id", ObjectId(movie_id))
        # remove review from user profile latest reviews list
        update_collection_item_dict("users", "_id", user["_id"],
                                    "$pull", "user_latest_reviews",
                                    "review_for_id", ObjectId(movie_id))
        flash("Review deleted")
        update_average_rating(ObjectId(movie_id))
        return redirect(url_for('view_reviews', movie_id=movie_id))
    else:
        flash("Movie and/or Review not found")
        return redirect(url_for('home'))


# watched & want to watch list control
@app.route("/user/watched-movie/<movie_id>/add")
def add_watched_movie(movie_id):
    """
    add movie id, name and release year in dict to user watched list
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to do this")
        return redirect(url_for("signin"))
    create_and_add_mini_movie_dict(movie_id, "movies_watched")
    flash("Movie added to your Watched List")
    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/user/watched-movie/<movie_id>/remove")
def remove_watched_movie(movie_id):
    """
    delete mini movie dict from user watched list
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to do this")
        return redirect(url_for("signin"))
    update_collection_item_dict("users", "_id", ObjectId(session["id"]),
                                "$pull", "movies_watched", "movie_id",
                                ObjectId(movie_id))
    flash("Movie Removed from your Watched List")
    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/user/want-to-watch/<movie_id>/add")
def add_want_to_watch_movie(movie_id):
    """
    add movie id, name and release year in dict to user want to watch list
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to do this")
        return redirect(url_for("signin"))
    create_and_add_mini_movie_dict(movie_id, "movies_to_watch")
    flash("Movie added to your Want To Watch List")
    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/user/want-to-watch/<movie_id>/remove")
def remove_want_to_watch_movie(movie_id):
    """
    delete mini movie dict from user want to watch list
    """
    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to do this")
        return redirect(url_for("signin"))
    update_collection_item_dict("users", "_id", ObjectId(session["id"]),
                                "$pull", "movies_to_watch", "movie_id",
                                ObjectId(movie_id))
    flash("Movie Removed from your Want To Watch List")
    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """
    GET - Check if user is signed in, find user info and bind render to page
    POST - inset message into database in a dict with user feedback
    """
    if request.method == "POST":
        mongo.db.messages.insert_one({
            "sender_name": request.form.get("full-name"),
            "sender_email": request.form.get("email"),
            "message": request.form.get("message"),
            "datetime_sent": datetime.now()
        })
        flash("Message Sent Successfully!")
    user_signed_in = is_signed_in()
    if user_signed_in:
        user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                       {"firstname": 1, "lastname": 1,
                                       "email": 1})
    else:
        user = None
    return render_template("contact.html", user=user)


@app.route("/movies")
def view_all_movies():
    """
    find all movies, store required information, sort by movie title and 
    render to the page
    """
    movies = mongo.db.movies.find({}, {"movie_title": 1, "image_link": 1,
                                       "release_date": 1}).sort("movie_title")
    return render_template("view-all-movies.html", movies=movies)


# error handlers
@app.errorhandler(400)
def bad_request(e):
    message = "A Bad Request was made"
    return render_template('error.html', error=400, message=message), 400


@app.errorhandler(403)
def forbidden(e):
    message = "This action is Forbidden!"
    return render_template('error.html', error=403, message=message), 403


@app.errorhandler(404)
def not_found(e):
    message = "Sorry, we can't find the page you are looking for!"
    return render_template('error.html', error_code=404, message=message), 404


@app.errorhandler(408)
def request_timeout(e):
    message = "The Server didn't recieve a complete request is time. Please try \
        again"
    return render_template('error.html', error_code=408, message=message), 408


@app.errorhandler(429)
def too_many_requests(e):
    message = "The Server recieved too many Requests. Try again later"
    return render_template('error.html', error_code=429, message=message), 429


@app.errorhandler(500)
def internal_server_error(e):
    message = "Sorry, its not you, its me! I have had an internal server \
        error! Please give me some time and we can try again"
    return render_template('error.html', error_code=500, message=message), 500


@app.errorhandler(Exception)
def other_error(e):
    message = "Something went wrong! If this is a reoccuring error then \
        get in touch"
    return render_template('error.html', error_code=e, message=message)


# application running instructions by retieving hidden env variables
if __name__ == "__main__":
    # retrieve the hidden env values and set them in variables
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)  # this only used in development to debug
