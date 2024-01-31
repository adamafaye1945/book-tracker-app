from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from book_database import DatabaseConnection
import json
from flask_cors import CORS
import uuid
import os
from User import User

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)
my_database = DatabaseConnection()


@login_manager.user_loader
def load_user(user_id):
    userinfo = my_database.retrieve_user(user_id)
    user = User(*userinfo)
    return user


# initializing database
@app.route('/')
def index():
    return str(current_user.name)


@app.route("/get_book", methods=["GET"])
@login_required
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
@login_required
def add_book():
    try:
        data = request.get_json()
        bookId = data.get("bookId")
        book_name = data.get("title")
        author_name = data.get("author_name")
        imageUrl = data.get("imageUrl")
        averageRating = data.get("averageRating")
        if not bookId:
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
@login_required
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
    data = request.get_json()
    try:
        email = data.get("email")
        password = data.get("password")
        userinfo = my_database.authenticate(email, password)
        if userinfo:
            user = User(*userinfo)
            login_user(user)
            return jsonify(response=200, id=user.id, message=f"user with id {user.id} authenticated",
                           authenticated=True), 200
        raise ValueError("user not found")
    except ValueError as e:
        message = str(e)
        return jsonify(message=message, response=400), 400


@app.route("/logout")
def logout():
    old_user = current_user.name
    logout_user()
    return jsonify(message = f"{old_user} logged out")


@app.route("/add-user", methods=["POST"])
def add_user():
    try:
        data = request.get_json()
        id = uuid.uuid4()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        my_database.add_users(id=id, password=password, email=email, name=name)
        return jsonify(response=200, message="user was successfully added to database"), 200

    except ValueError as e:
        message = str(e)
        return json.dumps({"error": message}), 400


if __name__ == '__main__':
    app.run(debug=True)
