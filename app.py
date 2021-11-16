import os
from datetime import datetime, timedelta
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


def is_signed_in():
    if session and len(session) > 1 and session["id"]:
        return True
    else:
        return False


def create_single_review(movie, movie_id=None):
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
    # doesn't have a MongoDb _id yet
    if movie_id is None:
        review["review_for_id"]: movie["_id"]
    else:
        review["review_for_id"]: movie_id
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


def generate_average_rating(movie_id, movie=None):
    if movie is None:
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
        new_average_rating = round(total_review_score/(len(
                                        movie["reviews"])), 2)
    else:
        new_average_rating = 0
    # set the variable in the DB to the new value
    mongo.db.movies.update_one({"_id": ObjectId(
                                movie["_id"])},
                               {"$set": {"average_rating":
                                         new_average_rating}})


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


def generate_matching_movies_list(collection, collection_list_name, 
                                  user_list, sort_list_by_key=None, 
                                  new_list_length=None, movie_id=None):
    """
    function to compare 2 lists matching values under append any matching
    dicts to a new list.
    """
    storage_list = []
    for item in collection:
        if item["_id"] != movie_id:
            if set(user_list).intersection(item[collection_list_name]):
                storage_list.append(item)
    if sort_list_by_key:
        storage_list = sorted(storage_list, key=lambda d: d[sort_list_by_key])
    elif sort_list_by_key and new_list_length:
        storage_list = sorted(storage_list, key=lambda d: d[sort_list_by_key])[:new_list_length]
    return storage_list


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


def generate_new_movie_dict(movie_id=None, update=None):
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
        new_movie["reviews"]: []
        new_movie["latest_reviews"]: []
        new_movie["created_by"]: session['id']
        new_movie["is_part_of_series"]: False
        new_movie["average_rating"]: 0.0
    add_series_information_to_dict(new_movie)
    if movie_id and request.form.get("submit-movie-review"):
        review = create_single_review(new_movie, movie_id)
        new_movie["reviews"].append(review)
    return new_movie


def add_series_information_to_dict(new_movie):
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
    generate mini movie dict and add to session user profile array
    """
    if movie is None:
        movie = find_one_with_key("movies", "_id", ObjectId(movie_id))

    new_mini_movie_dict = {
        "movie_id": movie["_id"],
        "movie_title": movie["movie_title"],
        "release_year": movie["release_date"].strftime('%Y')
    }

    update_collection_item("users", "_id", ObjectId(session["id"]), "$push",
                           array_name, new_mini_movie_dict)


def filter_movies_using_age_ratings(movie_list, user_age):
    storage_list = []
    for movie in movie_list:
        # any less than 12a, 12, 15 and 18 will be added to the list
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


def check_if_user_has_watched(movies_list, user):
    storage_list = [movie for movie in movies_list if movie["_id"] not in 
                    [movie["movie_id"] for movie in user["movies_watched"]]]
    return storage_list


# ---------- app.route ----------
@app.route("/")
@app.route("/home")
def home():
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
    # initialize empty lists for storage
    movies_for_you = []
    want_to_watch = []

    if is_signed_in():
        try:
            user = mongo.db.users.find_one({"_id": ObjectId(session["id"])},
                                           {"password_hash": 0})

            if user:
                movies_for_you = generate_matching_movies_list(
                                    movies, "genre", user["favourite_genres"],
                                    'average_rating', 15)
                # calculate age of user
                age = (datetime.now() - datetime.strptime(
                                            user["dob"], '%Y-%m-%d')).days
                movies_for_you = filter_movies_using_age_ratings(
                                    movies_for_you, age)
                movies_for_you = check_if_user_has_watched(
                                    movies_for_you, user)
                # generate want_to_watch list
                want_to_watch = [movie for movie in movies if movie["_id"] in
                                 [movie["movie_id"] for movie in
                                 user["movies_to_watch"]]]
                want_to_watch = sorted(want_to_watch, key=lambda d: d[
                                        'average_rating'])[:15]
        except Exception:
            pass

    return render_template("home.html", all_movies=all_movies,
                           highest_rated=highest_rated,
                           latest_releases=latest_releases,
                           movies_for_you=movies_for_you,
                           want_to_watch=want_to_watch)


@app.route("/search", methods=["POST"])
def movie_title_search():
    query = request.form.get("movie_title_search")
    searched_movies = list(mongo.db.movies.find(
                            {"$text": {"$search": query}}).sort("movie_title"))
    return render_template("movie-search.html", movies=searched_movies)


# genre management
@app.route("/genre")
def get_all_genre():
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))
    genre_list = list(mongo.db.genre.find().sort("genre_name"))
    return render_template("genre-management.html", genre_list=genre_list)


@app.route("/genre/add", methods=["POST"])
def add_genre():
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
    function to update a genre name in the DB
    """
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))

    new_genre_name = request.form.get("replacement-genre-name")
    # check if genre name already exists
    existing_name = mongo.db.genre.find_one({"genre_name": new_genre_name})
    if existing_name:
        flash("There is a Genre with this name already")
        return redirect(url_for('get_all_genre'))
    # updating the informatiion in the DB using the _id to find the documnet
    try:
        genre = mongo.db.genre.find_one({'_id': ObjectId(genre_id)})
        if genre:
            mongo.db.genre.update({"_id": ObjectId(genre_id)}, {
                                        "genre_name": new_genre_name.lower()})
            flash("Genre Updated")
        else:
            flash("Genre Not Found to Update")
        return redirect(url_for('get_all_genre'))
    except Exception as e:
        flash("Genre Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report a "
              "reoccurring problem")
    return redirect(url_for('get_all_genre'))


@app.route("/genre/<genre_id>/delete")
def delete_genre(genre_id):
    is_user_admin = is_admin()
    if not is_user_admin:
        return redirect(url_for("home"))
    try:
        genre = find_one_with_key("genre", "_id", ObjectId(genre_id))

        if genre:
            mongo.db.genre.remove_one({
                "_id": genre["_id"]
            })
            flash("Genre Deleted")
        else:
            flash("No Genre was found so nothing was deleted")
    except Exception as e:
        flash("Genre Not Found or Deleted")
        flash(str(e))
        flash("Please try again or get in touch to report a "
              "reoccurring problem")

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
        return redirect(url_for('profile'))

    genre_list = list(mongo.db.genre.find().sort("genre_name"))
    return render_template("signup.html", genre_list=genre_list)


# view user profile
@app.route("/profile")
def profile():

    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("Please sign in to access a User Profile")
        return redirect(url_for("signin"))

    try:
        user = mongo.db.users.find_one(
                {"_id": ObjectId(session["id"])},
                {"password_hash": 0})

        # generate suggested_movies list
        movies = list(mongo.db.movies.find({}, {"movie_title": 1,
                                                "image_link": 1,
                                                "genre": 1,
                                                "average_rating": 1,
                                                "age_rating": 1}))

        suggested_movies = generate_matching_movies_list(
                            movies, "genre", user["favourite_genres"],
                            'average_rating', 15)
        # calculate age of user
        age = (datetime.now() - datetime.strptime(
                                user["dob"], '%Y-%m-%d')).days
        suggested_movies = filter_movies_using_age_ratings(
                            suggested_movies, age)
        suggested_movies = check_if_user_has_watched(suggested_movies, user)

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
    except Exception as e:
        flash("User profile was not found")
        flash(str(e))
        flash("Please try again or get in touch to report a"
              " reoccurring problem")
        return redirect(url_for("home"))


@app.route("/profile/reviews/view")
def view_all_user_reviews():
    try:
        movies = mongo.db.movies.find({}, {"reviews": 1})
        reviews = []
        for movie in movies:
            for review in movie["reviews"]:
                if review["reviewer_id"] == session["id"]:
                    reviews.append(review)
        reviews = sorted(reviews, key=lambda d: d[
                                    'review_for'])
        return render_template("view-all-user-reviews.html",
                                reviews=reviews)
    except Exception as e:
        flash("Movies Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report "
              "a reoccurring problem")
        return redirect(url_for('view_all_movies'))

# edit user profile
@app.route("/profile/edit", methods=["GET", "POST"])
def edit_user_profile():

    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("Please sign in to Edit a User Profile")
        return redirect(url_for("signin"))

    if request.method == "POST":
        try:
            user = mongo.db.users.find_one(
                    {"_id": ObjectId(session['id'])},
                    {"password_hash": 0})

            requested_username = request.form.get("username").lower()

            existing_user = mongo.db.users.find_one(
                            {"username": requested_username.lower()},
                            {"password_hash": 0})

            if existing_user and requested_username != user["username"]:
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

            add_user_data_to_session_storage(updated_profile_dict,
                                                ObjectId(session["id"]))

            flash(f"Updated {session['user'].capitalize()} Account!")
            return redirect(url_for('profile'))

        except Exception as e:
            flash("User not Found")
            flash(str(e))
            flash("Please try again or get in touch to report"
                    " a reoccurring problem")
            return redirect(url_for('home'))
    try:
        user = find_one_with_key("users", "_id", ObjectId(session["id"]))
        user["dob"] = datetime.strptime(user["dob"], '%Y-%m-%d')
    except Exception as e:
        flash("User not Found")
        flash(str(e))
        flash("Please try again or get in touch to report "
                "a reoccurring problem")
        return redirect(url_for('home'))

    genre_list = list(mongo.db.genre.find().sort("genre_name"))
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
        flash("You do not have the required permissions to delete this"
              " profile")
        return redirect(url_for("home"))

    try:
        user = find_one_with_key("users", "_id", ObjectId(user_id))
    except Exception as e:
        flash("User Profile Was Not Deleted")
        flash(str(e))
        flash("Please try again or get in touch to report "
              "a reoccurring problem")
        return redirect(url_for('profile'))

    if user:
        mongo.db.users.remove({
            "_id": ObjectId(user_id)
        })
        username = session["user"].title()
        session.clear()
        flash(f"User Profile {username} Deleted")
        return redirect(url_for('home'))
    else:
        flash("No User account was found to delete")
    return redirect(url_for('profile'))


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



@app.route("/movie/add", methods=["GET", "POST"])
def create_movie():

    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to add a movie")
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
        movie = find_one_with_key("movies", "_id", ObjectId(new_id))
        if movie:
            flash(f"Movie {movie['movie_title'].title()} Created")
            if request.form.get("submit-movie-review"):
                new_review = create_single_review(movie)
                mongo.db.movies.update_one({"_id": ObjectId(movie["_id"])},
                                        {"$push": {"reviews": new_review}})
                create_and_add_mini_movie_dict(new_id, "movies_reviewed",
                                            movie)
                add_review_to_latest_reviews_dicts(
                    movie, create_single_review(movie, movie["_id"]))
                generate_average_rating(ObjectId(new_id))
                flash("with your Review Added")
            return redirect(url_for("view_movie", movie_id=new_id))
        else:
            flash("An error occured and the Movie was not created")
        return redirect(url_for("create_movie"))

    genre_list = list(mongo.db.genre.find().sort("genre_name"))
    age_ratings = mongo.db.age_ratings.find().sort("uk_rating_order")
    return render_template("create-movie.html", genre_list=genre_list,
                            age_ratings=age_ratings)


def check_key_in_array_of_dicts(array_to_check, key, value_to_check_against):
    for item in array_to_check:
        if value_to_check_against == item[key]:
            return True
    return False


@app.route("/movie/<movie_id>/view")
def view_movie(movie_id):
    try:
        movie = mongo.db.movies.find_one(
                {'_id': ObjectId(movie_id)})
    except Exception as e:
        flash("Movie Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report "
              "a reoccurring problem")
        return redirect(url_for('view_all_movies'))

    user_want_to_watch = False
    user_watched = False
    user_reviewed = False

    if is_signed_in():
        try:
            user = mongo.db.users.find_one(
                {"_id": ObjectId(session["id"])},
                {"_id": 0, "movies_watched": 1, "movies_to_watch": 1,
                 "movies_reviewed": 1})
        except Exception:
            pass

        if user:
            user_reviewed = check_key_in_array_of_dicts(
                              user["movies_reviewed"],
                              "movie_id", movie["_id"])

            user_watched = check_key_in_array_of_dicts(
                            user["movies_watched"],
                            "movie_id", movie["_id"])

            user_want_to_watch = check_key_in_array_of_dicts(
                                  user["movies_to_watch"],
                                  "movie_id", movie["_id"])

    # generate similar_movies list
    movies = list(mongo.db.movies.find({}, {"genre": 1, "average_rating": 1,
                                            "movie_title": 1,
                                            "release_date": 1,
                                            "latest_reviews": 1,
                                            "image_link": 1}))
    similar_movies = generate_matching_movies_list(movies, "genre", movie["genre"], 'average_rating', 15, movie["_id"])

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
    try:
        movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
    except Exception as e:
        flash("Movie Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report "
              "a reoccurring problem")
        return redirect(url_for('view_all_movies'))

    if movie:
        # use id from movie["created_by"] to check if user created the profile
        is_user_allowed = is_correct_user(movie["created_by"])
        if not is_user_allowed:
            return redirect(url_for("home"))

        if request.method == "POST":
            updated_movie = generate_new_movie_dict(movie_id, "update")
            mongo.db.movies.update_one({"_id": ObjectId(movie_id)}, {"$set": updated_movie})

            if request.form.get("submit-movie-review"):
                create_and_add_mini_movie_dict(movie_id, "movies_reviewed",
                                               movie)
                add_review_to_latest_reviews_dicts(
                    movie, create_single_review(movie, movie["_id"]))
                generate_average_rating(ObjectId(movie_id))

            flash("Movie Profile Successfully Updated")
            return redirect(url_for("view_movie", movie_id=movie_id))

        genre_list = list(mongo.db.genre.find().sort("genre_name"))
        for genre in genre_list:
            if genre["genre_name"].lower() in movie["genre"]:
                genre["checked"] = True
        age_ratings = mongo.db.age_ratings.find().sort("uk_rating_order")
        # make into function??
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
        return redirect(url_for('view_all_movies'))


@app.route("/movie/<movie_id>/delete")
def delete_movie(movie_id):
    try:
        movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                         {"created_by": 1})
    except Exception as e:
        flash("Movie Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report "
              "a reoccurring problem")
        return redirect(url_for('view_all_movies'))

    if movie:
        # use id from movie["created_by"] field to check if user
        # created the profile
        is_user_allowed = is_correct_user(movie["created_by"])
        if not is_user_allowed:
            flash("You are not allowed to delete this movie")
            return redirect(url_for("home"))
        # remove movie from all users movies_reviewed, watched and to watch arrays
        mongo.db.users.update_many({}, {"$pull": {"movies_reviewed": {"movie_id": movie["_id"]}}})

        mongo.db.users.update_many({}, {"$pull": {"movies_watched": {"movie_id": movie["_id"]}}})

        mongo.db.users.update_many({}, {"$pull": {"movies_to_watch": {"movie_id": movie["_id"]}}})
        # remove movie from all users latest_reviews array
        mongo.db.users.update_many({}, {"$pull": {"user_latest_reviews": {"review_for_id": movie["_id"]}}})

        mongo.db.movies.remove({
            "_id": movie["_id"]
        })
        flash("Movie Deleted")

    else:
        flash("Movie Not Found So Not Deleted")
    return redirect(url_for('home'))


# review management
@app.route("/reviews/<movie_id>/view")
def view_reviews(movie_id):
    try:
        movie = find_one_with_key("movies", "_id", ObjectId(movie_id))
        movie_reviews = sorted(movie["reviews"], key=lambda d: d[
                                    'review_date'], reverse=True)
        return render_template("view-reviews.html", movie=movie,
                               movie_reviews=movie_reviews)
    except Exception as e:
        flash("Movie Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report "
              "a reoccurring problem")
        return redirect(url_for('view_all_movies'))


# use movie_if for this app.route not movie_title - request args **!
@app.route("/review/add", methods=["GET", "POST"])
def create_review():

    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to add a review")
        return redirect(url_for("signin"))

    if request.method == "POST":
        movie_id = request.form.get('selected-movie-id')

        if movie_id:
            try:
                movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                                 {"latest_reviews": 1,
                                                  "reviews": 1,
                                                  "movie_title": 1,
                                                  "release_date": 1})
            except Exception as e:
                flash("Movie Not Found")
                flash(str(e))
                flash("Please try again or get in touch to report a "
                      "reoccurring problem")
                return redirect(url_for('view_all_movies'))

            if movie:
                # check for previous review from user
                for review in movie["reviews"]:
                    if review["reviewer_id"] == session["id"]:
                        flash("You have already created a review "
                              "for this movie")
                        return redirect(url_for('edit_review',
                                        movie_id=movie["_id"],
                                        user_id=session["id"]))
                try:
                    user = find_one_with_key("users", "_id",
                                             ObjectId(session["id"]))
                except Exception as e:
                    flash("User Not Found")
                    flash(str(e))
                    flash("Please try again or get in touch to report "
                          "a reoccurring problem")
                    return redirect(url_for('view_reviews',
                                            movie_id=movie["_id"]))
                if user:
                    new_review = create_single_review(movie)
                    mongo.db.movies.update_one({"_id": ObjectId(
                                                movie["_id"])},
                                               {"$push": {
                                                "reviews": new_review}})
                    create_and_add_mini_movie_dict(movie_id, "movies_reviewed",
                                                   movie)
                    generate_average_rating(ObjectId(movie["_id"]))
                    add_review_to_latest_reviews_dicts(movie, new_review)
                else:
                    flash("No User was found so your review was not submitted")
                return redirect(url_for('view_reviews', movie_id=movie["_id"]))
            else:
                flash("Movie Not Found")
                flash("Please try again or get in touch to report "
                      "a reoccurring problem")
                return redirect(url_for('create_review'))

        else:
            requested_movie_name = request.form.get("selected-movie-title")

            flash(f"There is no movie called '{requested_movie_name.title()}' "
                  f"in the database.\nEither create a profile for this movie "
                  f"or try a different Movie Title")
        return redirect(url_for('create_review'))

    movie_id = request.args.get("movie_id")
    if movie_id:
        try:
            movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)},
                                             {"reviews": 1})
        except Exception as e:
            flash("Movie Not Found")
            flash(str(e))
            flash("Please try again or get in touch to report a"
                  " reoccurring problem")
            return redirect(url_for('view_all_movies'))
        if movie:
            # check for previous review from user
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


@app.route("/movie/<movie_id>/review/<user_id>/edit", methods=["GET", "POST"])
def edit_review(movie_id, user_id):
    is_user_allowed = is_correct_user(user_id)
    if not is_user_allowed:
        return redirect(url_for('view_reviews', movie_id=movie_id))

    if request.method == "POST":
        try:
            movie = find_one_with_key("movies", "_id", ObjectId(movie_id))
        except Exception as e:
            flash("Movie Not Found")
            flash(str(e))
            flash("Please try again or get in touch to report a"
                  " reoccurring problem")
            return redirect(url_for('view_all_movies'))
        if movie:
            updated_review = create_single_review(movie)

            update_collection_item_dict("movies", "_id", ObjectId(movie_id),
                                        "$pull", "reviews", "reviewer_id",
                                        user_id)

            mongo.db.movies.update_one({"_id": ObjectId(movie_id)},
                                       {"$push": {"reviews": updated_review}})

            add_review_to_latest_reviews_dicts(movie, updated_review)
            generate_average_rating(ObjectId(movie["_id"]))

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
        flash("You don't have permission to delete this review")
        return redirect(url_for('home'))
    try:
        review = find_review(movie_id, user_id)
    except Exception as e:
        flash("Review Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report a"
              " reoccurring problem")
        return redirect(url_for('home'))

    if review:
        # remove review from movie profile reviews list using review_date
        update_collection_item_dict("movies", "_id", ObjectId(movie_id),
                                    "$pull", "reviews",
                                    "review_date",
                                    review["review_date"])
        # remove review from movie profile latest reviews list using review_date
        update_collection_item_dict("movies", "_id", ObjectId(movie_id),
                                    "$pull", "latest_reviews", "review_date",
                                    review["review_date"])
        # remove review from user profile reviews list
        update_collection_item_dict("users", "_id", ObjectId(user_id),
                                    "$pull", "movies_reviewed",
                                    "movie_id", ObjectId(movie_id))
        # remove review from user profile latest reviews list
        update_collection_item_dict("users", "_id", ObjectId(user_id),
                                    "$pull", "user_latest_reviews",
                                    "review_for_id", ObjectId(movie_id))
        flash("Review deleted")
        generate_average_rating(ObjectId(movie_id))
        return redirect(url_for('view_reviews', movie_id=movie_id))
    else:
        flash("Review not found")
        return redirect(url_for('home'))


# watched & want to watch list control
@app.route("/user/watched-movie/<movie_id>/add")
def add_watched_movie(movie_id):

    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to do this")
        return redirect(url_for("signin"))

    try:
        create_and_add_mini_movie_dict(movie_id, "movies_watched")
    except Exception as e:
        flash("Movie or User Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report a"
              " reoccurring problem")
        return redirect(url_for('profile'))
    flash("Movie added to your Watched List")
    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/user/watched-movie/<movie_id>/remove")
def remove_watched_movie(movie_id):

    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to do this")
        return redirect(url_for("signin"))
    try:
        update_collection_item_dict("users", "_id", ObjectId(session["id"]),
                                    "$pull", "movies_watched", "movie_id",
                                    ObjectId(movie_id))
    except Exception as e:
        flash("Movie or User Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report a"
              " reoccurring problem")
        return redirect(url_for('profile'))
    flash("Movie Removed from your Watched List")

    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/user/want-to-watch/<movie_id>/add")
def add_want_to_watch_movie(movie_id):

    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to do this")
        return redirect(url_for("signin"))
    try:
        create_and_add_mini_movie_dict(movie_id, "movies_to_watch")
    except Exception as e:
        flash("Movie or User Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report a"
              " reoccurring problem")
        return redirect(url_for('profile'))
    flash("Movie added to your Want To Watch List")

    return redirect(url_for("view_movie", movie_id=movie_id))


@app.route("/user/want-to-watch/<movie_id>/remove")
def remove_want_to_watch_movie(movie_id):

    user_signed_in = is_signed_in()
    if not user_signed_in:
        flash("You need to be signed in to do this")
        return redirect(url_for("signin"))
    try:
        update_collection_item_dict("users", "_id", ObjectId(session["id"]),
                                    "$pull", "movies_to_watch", "movie_id",
                                    ObjectId(movie_id))
    except Exception as e:
        flash("Movie or User Not Found")
        flash(str(e))
        flash("Please try again or get in touch to report a"
              " reoccurring problem")
        return redirect(url_for('profile'))
    flash("Movie Removed from your Want To Watch List")

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


@app.route("/movie/view_all")
def view_all_movies():
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
def internal_server_error(e):
    message = "Something went wrong! If this is a reoccuring error then \
        get in touch"
    return render_template('error.html', error_code=e, message=message)


# application running instructions by retieving hidden env variables
if __name__ == "__main__":
    # retrieve the hidden env values and set them in variables
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)  # this only used in development to debug
