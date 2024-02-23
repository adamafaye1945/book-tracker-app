from flask import Flask, jsonify, request, url_for, redirect
from book_database import DatabaseConnection
import json
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from User import User

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
        if json_data:
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
            if user_reflection and user_rating:
                my_database.adding_reflection_and_rating(
                    user_id=user_id,
                    reflection=user_reflection,
                    bookID=bookId,
                    rating=user_rating
                )
        return jsonify(message="addition to db was successful"), 200
    except ValueError as e:
        message = str(e)
        return jsonify(message=message, response=400), 400


@app.route("/delete", methods=["DELETE"])
def delete():
    try:
        id = request.args.get("id")
        my_database.delete_book(id)
        return jsonify(response=200, message=f"book {id} successfully deleted from database"), 200
    except ValueError as e:
        message = str(e)
        return jsonify(response=200, message=message), 400


@app.route("/login", methods=["GET"])
def login():
    try:
        email = request.args.get("email")
        password = request.args.get("password")
        userinfo = my_database.authenticate(email, password)
        if userinfo:
            user = User(*userinfo)
            access_token = create_access_token(user.id)
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
        my_database.add_users(password=password, email=email, name=name)
        return jsonify(response=200, message="user was successfully added to database"), 200

    except ValueError as e:
        message = str(e)
        return json.dumps({"error": message}), 400


if __name__ == '__main__':
    app.run(debug=True)
