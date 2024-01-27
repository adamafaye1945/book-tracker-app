from flask import Flask, jsonify, request
from  flask_login import LoginManager
from book_database import DatabaseConnection
import json
from flask_cors import CORS
import uuid
from User import User
app = Flask(__name__)
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)
my_database = DatabaseConnection()



@login_manager.user_loader
def load_user(user_id):
    userinfo = my_database.get(user_id)
    user = User(*userinfo)
    return user


# initializing database
@app.route('/')
def index():
    return "api"

@app.route("/get_book", methods=["GET"])
def get_book():
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
def delete():
    try:
        id = request.args.get("id")
        my_database.delete_book(id)
        return jsonify(response=200, message=f"book {id} successfully deleted from database"), 200
    except ValueError as e:
        message = str(e)
        return jsonify(response=200, message=message), 400


@app.route("/user-management", methods=["GET", "POST"])
def user_management():
    if request.method == "POST":
        try:
            data = request.get_json()
            id = uuid.uuid4()
            email = data.get("email")
            password = data.get("password")
            name = data.get("name")
            my_database.add_users(id=id, password=password, email=email, name = name)
            return jsonify(response=200, message="user was successfully added to database"), 200

        except ValueError as e:
            message = str(e)
            return json.dumps({"error": message}), 400
    try:
        email = request.args.get("email")
        password = request.args.get("password")
        user_id = my_database.authenticate(email, password)
        if user_id:
            return jsonify(response=200, id=user_id, message=f"user with id {user_id} authenticated",
                           authenticated=True), 200
        raise ValueError("user not found")
    except ValueError as e:
        message = str(e)
        return jsonify(message=message, response=400), 400


if __name__ == '__main__':
    app.run(debug=True)