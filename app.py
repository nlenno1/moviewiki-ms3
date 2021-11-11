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
    if session and session["is_superuser"] is True:
        return True
    return False


def is_correct_user(user_id_to_check):
    if session and session["id"] and (
      session["id"] == user_id_to_check or session["is_superuser"] is True):
        return True
    else:
        return False


def create_single_review(movie):
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


def update_collection_item_dict(collection_name, search_key, search_value,
                                update_operator, array_to_update,
                                array_search_key, array_search_value):
    mongo_prefix_select(collection_name).update_one(
        {search_key: search_value},
        {update_operator: {array_to_update:
                           {array_search_key: array_search_value}}})


def update_collection_item(collection_name, search_key, search_value,
                           update_operator, new_key, new_value):
    mongo_prefix_select(collection_name).update_one(
        {search_key: search_value},
        {update_operator: {new_key: new_value}})


def delete_collection_item(collection_name, search_key, search_value):
    mongo_prefix_select(collection_name).delete_one({search_key: search_value})


def add_collection_item(collection_name, search_key, search_value):
    mongo_prefix_select(collection_name).insert_one({search_key: search_value})


def generate_average_review_score(movie_id):
    movie = find_one_with_key("movies", "_id", movie_id)
    # generate an average reviews score
    total_review_score = 0
    # add all the review scores together from the data pulled from
    # the DB
    if len(movie["reviews"]) > 0:
        for review in movie["reviews"]:
            total_review_score += int(review["star_rating"])
        # divide the result by the amount of old scores plus 1 for the
        # score just added
        new_average_review_score = round(total_review_score/(len(
                                        movie["reviews"])), 2)
    else:
        new_average_review_score = 0
    # set the variable in the DB to the new value
    mongo.db.movies.update_one({"_id": ObjectId(
                                movie["_id"])},
                               {"$set": {"average_review_score":
                                         new_average_review_score}})


def convert_string_to_datetime(string_date):
    datetime_date = datetime.strptime(
        string_date, '%Y-%m-%d %H:%M:%S.%f')
    return datetime_date


def create_new_latest_reviews(review_list, new_review_dict,
                              to_compare_1, to_compare_2):
    new_review_list = [review for review in review_list if
                       review[to_compare_1] != to_compare_2]

    if len(new_review_list) > 2:
        new_review_list = new_review_list[0:2]
    new_review_list.append(new_review_dict)
    return new_review_list


def add_review_to_latest_reviews_dicts(movie, new_review_dict):
    user = find_one_with_key("users", "_id", ObjectId(session["id"]))

    user["user_latest_reviews"] = create_new_latest_reviews(
        user["user_latest_reviews"], new_review_dict, "review_for_id",
        movie["_id"])
    movie["latest_reviews"] = create_new_latest_reviews(
        movie["latest_reviews"], new_review_dict, "reviewer_id", session["id"])

    update_collection_item("users", '_id', ObjectId(session['id']), "$set",
                           "user_latest_reviews", user["user_latest_reviews"])
    update_collection_item("movies", '_id', ObjectId(movie['_id']), "$set",
                           "latest_reviews", movie["latest_reviews"])


def add_user_data_to_session_storage(user_dict, new_id=None):
    if new_id is None:
        session["id"] = str(user_dict['_id'])
    else:
        session["id"] = str(new_id)
    session['user'] = user_dict['username']
    session['email'] = user_dict['email']
    session['full-name'] = user_dict[
        'firstname'] + " " + user_dict['lastname']
    if "is_superuser" in user_dict:
        session['is_superuser'] = user_dict['is_superuser']


def consolidate_matching_array_dicts(list_1, list_2):
    """
    function to compare 2 lists matching values under append any matching
    dicts to a new list.
    """
    new_list = set(list_1).intersection(list_2)
    return new_list


def find_review_in_reviews_list(review_list, reviewer_id):
    movie_review = None
    if len(review_list) > 0:
        movie_review = [review for review in review_list
                        if review["reviewer_id"] == reviewer_id][0]
    return movie_review


def find_review(movie_id, reviewer_id):
    movie = find_one_with_key("movies", "_id", ObjectId(movie_id))
    movie_review = find_review_in_reviews_list(movie["reviews"], reviewer_id)
    return movie_review


def add_review_to_dict(new_movie):
    if request.form.get("submit-movie-review"):
        review = create_single_review(new_movie)
        review["review_for"] = new_movie["movie_title"]
        new_movie["reviews"].append(review)
        new_movie["latest_reviews"].append(review)
        new_movie["average_rating"] = review["star_rating"]


def generate_new_movie_dict():
    image_link = generate_movie_image_link()
    new_movie = {
            "movie_title": request.form.get("movie-title").lower(),
            "release_date": datetime.strptime(request.form.get(
                                              "release-date"), '%Y-%m-%d'),
            "age_rating": request.form.get("age-rating"),
            "duration": request.form.get("duration"),
            "genre": request.form.getlist("movie-genre"),
            "director": request.form.get("director").lower(),
            "cast_members": request.form.get("cast-members").lower().split(","),
            "movie_synopsis": request.form.get("movie-synopsis"),
            "movie_description": request.form.get("movie-description"),
            "image_link": image_link,
            "reviews": [],
            "latest_reviews": [],
            "created_by": session['id'],
            "is_part_of_series": False,
            "average_rating": 0.0
        }
    add_series_information_to_dict(new_movie)
    add_review_to_dict(new_movie)
    return new_movie


def generate_movie_image_link():
    if request.form.get("image-link"):
        image_link = request.form.get("image-link")
    else:
        image_link = "../static/img/movie-placeholder.png"
    return image_link


def add_series_information_to_dict(new_movie):
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


# ---------- app.route ----------
@app.route("/")
@app.route("/home")
def home():
    movies = list(mongo.db.movies.find({}, {"movie_title": 1,
                                            "average_rating": 1,
                                            "release_date": 1,
                                            "genre": 1,
                                            "image_link": 1}))
    # sorted alphabeticallly by title with max of 15
    all_movies = sorted(movies, key=lambda d: d['movie_title'])[:15]
    # sorted by average rating by title with max of 15
    highest_rated = sorted(movies, key=lambda d: d['average_rating'],
                           reverse=True)[:15]
    # sorted by release date by title with max of 15
    latest_releases = sorted(movies, key=lambda d: d['release_date'],
                             reverse=True)[:15]
    # initialize empty lists for storage
    movies_for_you = []
    want_to_watch = []

    if session and session["id"]:
        user = find_one_with_key("users", "_id", ObjectId(session["id"]))
        # generate suggested_movies list
        for item in movies:
            if set(user["favourite_genres"]).intersection(item["genre"]):
                movies_for_you.append(item)
        movies_for_you = sorted(movies_for_you, key=lambda d: d[
                                'average_rating'])[:15]
        # generate want_to_watch list
        for item in user["movies_to_watch"]:
            for movie in movies:
                if movie["movie_title"] == item:
                    want_to_watch.append(movie)
        want_to_watch = sorted(want_to_watch, key=lambda d: d[
                                'average_rating'])[:15]

    return render_template("home.html", all_movies=all_movies,
                           highest_rated=highest_rated,
                           latest_releases=latest_releases,
                           movies_for_you=movies_for_you,
                           want_to_watch=want_to_watch)


@app.route("/search")
def movie_title_search():
    query = request.form.get("movie_title_search")
    searched_movies = list(mongo.db.movies.find({"$text": {"$search": query}}))
    return render_template("movie-search.html", movies=searched_movies)


# genre management
@app.route("/genre")
def get_all_genre():
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))
    genre_list = list(mongo.db.genre.find())
    return render_template("genre-management.html", genre_list=genre_list)


@app.route("/genre/add", methods=["POST"])
def add_genre():
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))

    new_genre_name = request.form.get('genre-name')
    mongo.db.genre.insert_one({
        "genre_name": new_genre_name.lower()
    })
    flash("Genre " + new_genre_name.title() + " added!")
    return redirect(url_for('get_all_genre'))


@app.route("/genre/<genre_id>/update", methods=["POST"])
def update_genre(genre_id):
    """
    function to update a genre name in the DB
    """
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))

    new_genre_name = request.form.get("replacement-genre-name")
    # updating the informatiion in the DB using the _id to find the documnet
    try:
        genre = mongo.db.genres.find_one({'_id': ObjectId(genre_id)})
        if genre:
            mongo.db.genre.update({"_id": ObjectId(genre_id)}, {
                                        "genre_name": new_genre_name.lower()})
            flash("Genre Updated")
            return redirect(url_for('get_all_genre'))
    except:
        flash("An Error Occured")
        return redirect(url_for('get_all_genre'))


@app.route("/genre/<genre_id>/delete")
def delete_genre(genre_id):
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))
    mongo.db.genre.remove({
        "_id": ObjectId(genre_id)
    })
    flash("Genre Deleted")
    return redirect(url_for('get_all_genre'))


# user account management
# create user profile
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
            "password_hash": generate_password_hash(
                              request.form.get("password")),
            "firstname": request.form.get("firstname").lower(),
            "lastname": request.form.get("lastname").lower(),
            "dob": request.form.get("dob"),
            "email": request.form.get('email'),
            "favourite_genres": request.form.getlist('favourite-genre'),
            "date_joined":  datetime.now(),
            "is_superuser": False,
            # unfilled fields
            "movies_reviewed": [],
            "movies_watched": [],
            "movies_to_watch": [],
            "user_latest_reviews": [],
        }

        new_id = mongo.db.users.insert_one(register).inserted_id
        add_user_data_to_session_storage(register, new_id)

        # put the user into session and load profile page
        flash("Registration Successful " + session["user"].capitalize() + "!")
        return redirect(url_for('profile', user_id=session['id']))

    genre_list = mongo.db.genre.find()
    return render_template("signup.html", genre_list=genre_list)


# view/read user profile
@app.route("/profile/<user_id>", methods=["GET", "POST"])
def profile(user_id):

    is_user_allowed = is_correct_user(user_id)
    if not is_user_allowed:
        return redirect(url_for("home"))

    user = mongo.db.users.find_one(
            {"_id": ObjectId(user_id)},
            {"password_hash": 0})

    # generate suggested_movies list
    suggested_movies = []
    movies = list(mongo.db.movies.find())
    for item in movies:
        if set(user["favourite_genres"]).intersection(item["genre"]):
            suggested_movies.append(item)
    suggested_movies = sorted(suggested_movies, key=lambda d: d[
                                'average_rating'])[:15]

    user_latest_reviews = sorted(user["user_latest_reviews"], key=lambda d: d[
                          'review_date'], reverse=True)

    return render_template("profile.html", user=user,
                           suggested_movies=suggested_movies,
                           user_latest_reviews=user_latest_reviews)


# edit user profile
@app.route("/profile/<user_id>/edit", methods=["GET", "POST"])
def edit_user_profile(user_id):
    is_user_allowed = is_correct_user(user_id)
    if not is_user_allowed:
        return redirect(url_for("home"))

    if request.method == "POST":
        user = mongo.db.users.find_one({"_id": ObjectId(session['id'])},
                                       {"password_hash": 0})

        requested_username = request.form.get("username").lower()
        # change into conditional to compare user["username"] and
        # requested_username
        existing_user = mongo.db.users.find_one(
            {"username": requested_username.lower()},
            {"password_hash": 0})

        if existing_user and existing_user["username"] != user["username"]:
            flash("Username " + requested_username.capitalize() +
                  " already exists")
            return redirect(url_for("edit_user_profile",
                                    user_id=session['id']))

        updated_profile_dict = {
            "username": request.form.get("username").lower(),
            "firstname": request.form.get("firstname").lower(),
            "lastname": request.form.get("lastname").lower(),
            "dob": request.form.get("dob"),
            "email": request.form.get('email'),
            "favourite_genres": request.form.getlist('movie-genre')
        }

        mongo.db.users.update_one({"_id": ObjectId(session['id'])},
                                  {"$set": updated_profile_dict})

        add_user_data_to_session_storage(updated_profile_dict, ObjectId(
                                         session["id"]))

        flash(f"Successfully Updated {session['user'].capitalize()} Account!")
        return redirect(url_for('profile', user_id=session['id']))

    user = find_one_with_key("users", "_id", ObjectId(user_id))
    user["dob"] = datetime.strptime(user["dob"], '%Y-%m-%d')

    genre_list = mongo.db.genre.find()
    genre_list = sorted(genre_list, key=lambda d: d['genre_name'])
    for genre in genre_list:
        if genre["genre_name"].lower() in user["favourite_genres"]:
            genre["checked"] = True
    return render_template("edit-user-profile.html", genre_list=genre_list,
                           user=user)


# delete user profile
@app.route("/profile/<user_id>/delete")
def delete_user_profile(user_id):
    is_user_allowed = is_correct_user(user_id)
    if not is_user_allowed:
        return redirect(url_for("home"))

    mongo.db.users.remove({
        "_id": ObjectId(user_id)
    })
    username = session["user"].title()
    session.clear()
    flash(f"User Profile {username} Deleted")
    return redirect(url_for('home'))


# user account access
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # check if username is on the BD
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )
        if existing_user:
            if check_password_hash(existing_user["password_hash"],
                                   request.form.get("password")):

                add_user_data_to_session_storage(existing_user)

                flash("Welcome " + session["user"].capitalize())

                return redirect(url_for('profile', user_id=session['id']))
            else:
                flash("The information entered is incorrect")
                return redirect(url_for('signin'))

        else:
            flash("The information entered is incorrect")
            return redirect(url_for('signin'))

    return render_template("signin.html")


@app.route("/signout")
def signout():

    if not session["user"]:
        return redirect(url_for("signin"))

    flash("You have signed out")
    session.clear()
    return redirect(url_for('home'))


@app.route("/movie/add", methods=["GET", "POST"])
def create_movie():

    if not session["user"]:
        return redirect(url_for("signin"))

    if request.method == "POST":
        new_movie = generate_new_movie_dict()

        existing_movies = mongo.db.movies.find(
                          {"movie_title": new_movie["movie_title"]})
        if existing_movies:
            for movie in existing_movies:
                if movie["release_date"].strftime(
                  '%Y') == new_movie["release_date"].strftime('%Y'):
                    flash(f"There is already a movie called "
                          f"{new_movie['movie_title'].title()} which was "
                          f"released in "
                          f"{new_movie['release_date'].strftime('%Y')}")
                    flash("Either use the existing movie profile or change"
                          " the release year")
                    return redirect(url_for('view_all_movies'))

        new_id = mongo.db.movies.insert_one(new_movie).inserted_id

        if request.form.get("seen-movie-checkbox"):
            update_collection_item("users", "_id", ObjectId(session["id"]),
                                   "$push", "movies_watched",  new_id)

        if request.form.get("submit-movie-review"):
            update_collection_item("users", "_id", ObjectId(session["id"]),
                                   "$push", "movies_reviewed",
                                   ObjectId(new_id))

        update_collection_item("users", '_id', ObjectId(session['id']), "$set",
                               "user_latest_reviews", new_movie[
                                   "latest_reviews"])

        flash("New Movie Added")
        return redirect(url_for("view_movie", movie_id=new_id))

    genre_list = mongo.db.genre.find()
    return render_template("create-movie.html", genre_list=genre_list)


def check_key_in_array_of_dicts(array_to_check, key, value_to_check_against):
    for item in array_to_check:
        if value_to_check_against == item[key]:
            return True
    return False


@app.route("/movie/<movie_id>/view")
def view_movie(movie_id):
    # add try except
    movie = mongo.db.movies.find_one(
            {'_id': ObjectId(movie_id)})

    user_want_to_watch = False
    user_watched = False
    user_reviewed = False

    if session["user"]:
        user = mongo.db.users.find_one(
            {"_id": ObjectId(session["id"])},
            {"_id": 0, "movies_watched": 1, "movies_to_watch": 1,
             "movies_reviewed": 1})

        user_reviewed = check_key_in_array_of_dicts(user["movies_reviewed"],
                                                   "movie_id", movie["_id"])

        user_watched = check_key_in_array_of_dicts(user["movies_watched"],
                                                   "movie_id", movie["_id"])

        user_want_to_watch = check_key_in_array_of_dicts(
                            user["movies_to_watch"], "movie_id", movie["_id"])

    # generate similar_movies list - make into function
    similar_movies = []
    movies = list(mongo.db.movies.find())
    for item in movies:
        if set(movie["genre"]).intersection(item["genre"]):
            similar_movies.append(item)
    similar_movies = sorted(similar_movies, key=lambda d: d[
                        'average_rating'], reverse=True)[:15]

    movie__genre_text_list = ', '.join(name.title() for name in movie["genre"])
    movie["genre"] = movie__genre_text_list
    latest_reviews = sorted(movie["latest_reviews"], key=lambda d: d[
                        'review_date'], reverse=True)

    return render_template("view-movie.html", movie=movie,
                           user_watched=user_watched,
                           user_want_to_watch=user_want_to_watch,
                           similar_movies=similar_movies,
                           latest_reviews=latest_reviews,
                           user_reviewed=user_reviewed)


@app.route("/movie/<movie_id>/edit", methods=["GET", "POST"])
def edit_movie(movie_id):
    # add try except
    # movie = mongo.bd.movies.find_one({"_id": ObjectId(movie_id)},
    #                                  {"created_by": 1})

    # use user id for movie["created_by"] field rather than usernames
    # is_user_allowed = is_correct_user(movie["created_by"])
    # if not is_user_allowed:
    #    return redirect(url_for("home"))

    if request.method == "POST":
        updated_movie = generate_new_movie_dict()
        mongo.db.movies.update({"_id": ObjectId(movie_id)}, updated_movie)
        if request.form.get("submit-movie-review"):
            update_collection_item("users", "_id", ObjectId(session["id"]),
                                   "$push", "movies_reviewed",
                                   ObjectId(movie_id))

        flash("Movie Profile Successfully Updated")
        return redirect(url_for("view_movie", movie_id=movie_id))

    movie = find_one_with_key("movies", "_id", ObjectId(movie_id))
    genre_list = list(mongo.db.genre.find().sort("genre_name"))
    age_ratings = mongo.db.uk_age_ratings.find().sort("uk_rating_order")
    for genre in genre_list:
        if genre["genre_name"].lower() in movie["genre"]:
            genre["checked"] = True
    # make into function - list from array of dicts with key
    movie_reviewers_id_list = []
    for review in movie["reviews"]:
        movie_reviewers_id_list.append(review["reviewer_id"])

    cast_members_string = ','.join(name.title() for name in movie[
                            "cast_members"])
    return render_template("edit-movie.html", genre_list=genre_list,
                           movie=movie, age_ratings=age_ratings,
                           cast_members_string=cast_members_string,
                           movie_reviewers_id_list=movie_reviewers_id_list)


@app.route("/movie/<movie_id>/delete")
def delete_movie(movie_id):
    # movie = mongo.bd.movies.find_one({"_id": ObjectId(movie_id)},
    #                                  {"created_by": 1})

    # use user id for movie["created_by"] field rather than usernames
    # is_user_allowed = is_correct_user(movie["created_by"])
    # if not is_user_allowed:
    #    return redirect(url_for("home"))

    mongo.db.movies.remove({
        "_id": ObjectId(movie_id)
    })
    flash("Movie Deleted")
    return redirect(url_for('home'))


# review management
@app.route("/reviews/<movie_id>/view")
def view_reviews(movie_id):
    # add try except
    movie = find_one_with_key("movies", "_id", ObjectId(movie_id))
    movie_reviews = sorted(movie["reviews"], key=lambda d: d[
                                'review_date'], reverse=True)
    list(movie)
    return render_template("view-reviews.html", movie=movie,
                           movie_reviews=movie_reviews)


# use movie_if for this app.route not movie_title - request args **!
@app.route("/review/add", methods=["GET", "POST"])
def create_review():

    if not session["user"]:
        return redirect(url_for("signin"))

    if request.method == "POST":
        movie_id = request.form.get('selected-movie-id')

        if movie_id:
            movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                             {"latest_reviews": 1,
                                              "reviews": 1,
                                              "movie_title": 1,
                                              "release_date": 1})

            # check for previous review from user
            for review in movie["reviews"]:
                if review["reviewer_id"] == session["id"]:
                    flash("You have already created a review for this movie")
                    return redirect(url_for('edit_review',
                                    movie_id=movie["_id"],
                                    user_id=session["id"]))

            new_review = create_single_review(movie)
            mongo.db.movies.update_one({"_id": ObjectId(
                                        movie["_id"])},
                                       {"$push": {"reviews": new_review}})

            create_and_add_mini_movie_dict(movie_id, "movies_reviewed", movie)

            generate_average_review_score(ObjectId(movie["_id"]))

            add_review_to_latest_reviews_dicts(movie, new_review)

            return redirect(url_for('view_reviews', movie_id=movie["_id"]))

        else:
            requested_movie_name = request.form.get("selected-movie-title")

            flash(f"There is no movie called '{requested_movie_name.title()}' "
                  f"in the database.\nEither create a profile for this movie "
                  f"or try a different Movie Title")
        return redirect(url_for('create_review'))

    movie_id = request.args.get("movie_id")
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                     {"reviews": 1})
    # check for previous review from user
    for review in movie["reviews"]:
        if review["reviewer_id"] == session["id"]:
            flash("You have already created a review for this movie")
            return redirect(url_for('edit_review',
                            movie_id=movie["_id"],
                            user_id=session["id"]))
    movie_title_list = mongo.db.movies.find({}, {"movie_title": 1,
                                                 "release_date": 1})

    return render_template(
        "create-review.html", movie_title_list=movie_title_list,
        selected_movie_id=movie_id)


@app.route("/movie/<movie_id>/review/<user_id>/edit", methods=["GET", "POST"])
def edit_review(movie_id, user_id):
    is_user_allowed = is_correct_user(user_id)
    if not is_user_allowed:
        return redirect(url_for('view_reviews', movie_id=movie_id))

    if request.method == "POST":
        movie = find_one_with_key("movies", "_id", ObjectId(movie_id))

        updated_review = create_single_review(movie)

        update_collection_item_dict("movies", "_id", ObjectId(movie_id),
                                    "$pull", "reviews", "reviewer_id",
                                    user_id)

        mongo.db.movies.update_one({"_id": ObjectId(movie_id)},
                                   {"$push": {"reviews": updated_review}})

        add_review_to_latest_reviews_dicts(movie, updated_review)

        return redirect(url_for('view_reviews', movie_id=movie_id))
    # condense this to one process
    movie = find_one_with_key("movies", "_id", ObjectId(movie_id))
    review = find_review_in_reviews_list(movie["reviews"], user_id)

    return render_template(
        "edit-review.html",
        selected_movie=movie, movie_review=review)


@app.route("/movie/<movie_id>/review/<user_id>/delete")
def delete_review(movie_id, user_id):

    is_user_allowed = is_correct_user(user_id)
    if not is_user_allowed:
        return redirect(url_for('view_reviews', movie_id=movie_id))

    review = find_review(movie_id, user_id)
    # remove review from movie profile reviews list
    update_collection_item_dict("users", "_id", ObjectId(session["id"]),
                                "$pull", "movies_reviewed", "movie_id",
                                ObjectId(movie_id))
    # remove review from movie profile latest reviews list
    update_collection_item_dict("movies", "_id", ObjectId(movie_id),
                                "$pull", "latest_reviews", "review_date",
                                review["review_date"])
    # remove review from movie profile latest reviews list
    update_collection_item("users", "_id", ObjectId(session['id']),
                           "$pull", "movies_reviewed", ObjectId(movie_id))

    # needs to be changed to a more suitable field
    update_collection_item_dict("users", "_id", ObjectId(session['id']),
                                "$pull", "user_latest_reviews", "reviewed_for",
                                movie_id)

    flash("Review deleted")
    movie = find_one_with_key("movies", "_id", ObjectId(movie_id))
    generate_average_review_score(ObjectId(movie["_id"]))
    return redirect(url_for('view_reviews', movie_id=movie["_id"]))


def create_and_add_mini_movie_dict(movie_id, array_name, movie=None):
    if movie is None:
        movie = find_one_with_key("movies", "_id", ObjectId(movie_id))

    new_mini_movie_dict = {
        "movie_id": movie["_id"],
        "movie_title": movie["movie_title"],
        "release_year": movie["release_date"].strftime('%Y')
    }

    update_collection_item("users", "_id", ObjectId(session["id"]), "$push",
                           array_name, new_mini_movie_dict)


# watched & want to watch list control
@app.route("/user/watched-movie/<movie_id>/add")
def add_watched_movie(movie_id):

    if not session["user"]:
        return redirect(url_for("signin"))

    create_and_add_mini_movie_dict(movie_id, "movies_watched")

    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/user/watched-movie/<movie_id>/remove")
def remove_watched_movie(movie_id):

    if not session["user"]:
        return redirect(url_for("signin"))

    update_collection_item_dict("users", "_id", ObjectId(session["id"]),
                                "$pull", "movies_watched", "movie_id",
                                ObjectId(movie_id))

    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/user/want-to-watch/<movie_id>/add")
def add_want_to_watch_movie(movie_id):

    if not session["user"]:
        return redirect(url_for("signin"))

    create_and_add_mini_movie_dict(movie_id, "movies_to_watch")

    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/user/want-to-watch/<movie_id>/remove")
def remove_want_to_watch_movie(movie_id):

    if not session["user"]:
        return redirect(url_for("signin"))

    update_collection_item_dict("users", "_id", ObjectId(session["id"]),
                                "$pull", "movies_to_watch", "movie_id",
                                ObjectId(movie_id))

    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        mongo.db.messages.insert_one({
            "sender_name": request.form.get("full-name"),
            "sender_email": request.form.get("email"),
            "message": request.form.get("message"),
            "datetime_sent": datetime.now()
        })
        flash("Message Sent Successfully!")

    return render_template("contact.html")


@app.route("/movies/view_all")
def view_all_movies():
    movies = mongo.db.movies.find({}, {"movie_title": 1, "image_link": 1})
    return render_template("view-all-movies.html", movies=movies)


# application running instructions by retieving hidden env variables
if __name__ == "__main__":
    # retrieve the hidden env values and set them in variables
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)  # this only used in development to debug
