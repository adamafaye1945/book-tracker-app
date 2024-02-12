from flask import Flask, jsonify, request
from book_database import DatabaseConnection
import json
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from User import User

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")
jwt = JWTManager(app)
CORS(app)
my_database = DatabaseConnection()


@app.route('/')
def index():
    return str(current_user.name)


@app.route("/get_book", methods=["GET"])
@jwt_required()
def get_book():
    # route will return a book json
    try:
        id = request.args.get("id")
        data = my_database.select_single_row_table(id=id, table='books_data')
        if data:
            json_data = {
                "Bookid": data[0],
                "author_name": data[1],
                "bookName": data[2],
                "imageURL": data[3],
                "averageRating": data[4]
            }
            return jsonify(book_data=json_data, response=200), 200
        raise ValueError("book not found")
    except ValueError as e:
        message = str(e)
        return jsonify(message=message, response=400), 400


@app.route("/add_book", methods=["POST"])
@jwt_required()
def add_book():
    try:
        data = request.get_json()
        bookId = data.get("bookId")
        book_name = data.get("title")
        author_name = data.get("author_name")
        imageUrl = data.get("imageUrl")
        averageRating = data.get("averageRating")
        if not bookId or not book_name or not author_name:
            raise ValueError("missing book id information, if unknown enter them as 'NULL', also check params")
        my_database.add_book_in_book_data(
            bookId=bookId,
            author_name=author_name,
            image_url=imageUrl,
            averageRating=averageRating,
            book_name=book_name
        )
        return jsonify(code=200, message="Book has been successfully added to database"), 200

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
