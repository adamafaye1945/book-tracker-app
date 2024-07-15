from flask import Flask, jsonify, request, url_for, redirect
from book_database import DatabaseConnection
import json
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from User import User
from datetime import timedelta
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")
jwt = JWTManager(app)
CORS(app)
my_database = DatabaseConnection()



@app.route('/')
@jwt_required()
def index():

    current_user = get_jwt_identity()
    return str(current_user)


@app.route("/get_book", methods=["GET"])
@jwt_required()
def get_book():
    id = get_jwt_identity()
    try:
        json_data = my_database.get_books(id)
        if len(json_data) > 0:
            return jsonify(book_data=json_data, response=200), 200
        return jsonify(book_data=[], response = 200), 200
    except ValueError as e:

        return jsonify(message="error", response=400), 400


@app.route("/add_book", methods=["POST"])
@jwt_required()
def add_book():
    data_bulk = request.get_json()
    user_id = get_jwt_identity()

    try:
        for data in data_bulk:
            bookId = data["bookId"]
            # sign rom client to delete a book
            if data["untracked"] == True:
                my_database.delete_book(bookId)
            else:
                book_name = data["title"]
                author_name = data["author_name"]
                imageUrl = data["imageUrl"]
                averageRating = data["averageRating"]
                publisher = data["publisher"]
                user_rating = data["userRating"]
                user_reflection = data["reflection"]

                if not bookId or not book_name or not author_name:
                    raise ValueError("missing book id information, if unknown enter them as 'NULL', also check params")
                my_database.add_book_in_book_data(
                    bookId=bookId,
                    author_name=author_name,
                    image_url=imageUrl,
                    averageRating=averageRating,
                    book_name=book_name,
                    publisher = publisher
                )
                my_database.adding_reflection_and_rating(
                    user_id=user_id,
                    reflection=user_reflection,
                    bookID=bookId,
                    rating=user_rating
                )
        return jsonify(message="db was successfully updated"), 200
    except ValueError as e:
        message = str(e)
        return jsonify(message=message, response=400), 400







@app.route("/login", methods=["GET"])
def login():
    try:
        email = request.args.get("email")
        password = request.args.get("password")
        userinfo = my_database.authenticate(email, password)
        if userinfo:
            user = User(*userinfo)
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=20))
            return jsonify(id=user.id,
                           name=user.name,
                           access_token=access_token), 200

        raise ValueError("User not found")
    except ValueError:
        return jsonify(message="user not found"), 400


@app.route("/logout")
def logout():
    pass


@app.route("/add_user", methods=["POST"])
def add_user():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        if my_database.retrieve_user(email):
            return jsonify( message = "user already exist"), 409
        my_database.add_users(password=password, email=email, name=name)
        return jsonify( message="user was successfully added to database"), 200

    except ValueError as e:
        message = str(e)
        return json.dumps({"error": message}), 400
@app.route("/add_friend", methods= ["POST"])
@jwt_required()

def add_friend():
    id = get_jwt_identity()
    try:
        data = request.get_json()
        friend = data.get("friend_id")
        friend_a_user = my_database.retrieve_user(id=friend)
        if not friend_a_user:
            raise ValueError ('user is not in the database')
        if my_database.create_frienship(userid=id, new_friend=friend_a_user):
            return jsonify(message="friendship set!"), 200
        return jsonify(message ="you can't add yourself"), 400
    except ValueError as e:
        message = str(e)
        return jsonify(message=message, response=400), 400

if __name__ == '__main__':
    app.run(debug=True)
