from flask import Flask, jsonify, request, abort
from book_database import DatabaseConnection
import json
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)

book_data_base = DatabaseConnection()


# initializing database
@app.route('/')
def index():
    return "api for books"


@app.route("/get_book", methods=["GET"])
def get_book():
    try:
        id = request.args.get("id")
        data = book_data_base.select_single_row_table(id=id, table='books_data')
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
@cross_origin()
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
        book_data_base.add_book_in_book_data(
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
        book_data_base.delete_book(id)
        return jsonify(response=200, message=f"book {id} successfully deleted from database"), 200
    except ValueError as e:
        message = str(e)
        return jsonify(response=200, message=message), 400


@app.route("/user-management", methods=["GET", "POST"])
def user_management():
    if request.method == "POST":
        try:
            data = request.get_json()
            id = data.get("id")
            email = data.get("email")
            password = data.get("password")
            book_data_base.add_users(id, email, password)
            return jsonify(response=200, message="user was successfully added to database"), 200
        except ValueError as e:
            message = str(e)
            return json.dumps({"error": message}), 400
    try:
        email = request.args.get("email")
        password = request.args.get("password")
        user_id = book_data_base.authenticate(email, password)
        if user_id:
            return jsonify(response=200, id=user_id, message=f"user with id {user_id} authenticated",
                           authenticated=True), 200
        raise ValueError("user not found")
    except ValueError as e:
        message = str(e)
        return jsonify(message=message, response=400), 400


if __name__ == '__main__':
    app.run(debug=True)