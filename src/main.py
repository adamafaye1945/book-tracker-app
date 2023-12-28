from flask import Flask, jsonify, request, abort
from book_database import DatabaseConnection
import json

app = Flask(__name__)

book_data_base = DatabaseConnection()


# initializing database
@app.route('/')
def index():
    return "api for books"


@app.route("/get_book", methods=["GET"])
def get_book():
    try:
        id = request.args.get("id")
        data = book_data_base.select_single_row(id)[0]
        json_data = {
            "id": data[0],
            "author_name": data[1],
            "ISBN": data[2],
            "BookName": data[3]
        }
        return jsonify(book_data=json_data, response=200), 200
    except:
        return jsonify(code=400, message="error getting book"), 400


@app.route("/add_book", methods=["POST"])
def add_book():
    try:
        data = request.get_json()
        book_name = data.get("book_name")
        isbn = data.get("isbn")
        author_name = data.get("author_name")
        if not book_name or not isbn or not author_name:
            abort(400, description="Missing required book information")
        book_data_base.add_book_in(book_name=book_name, isbn=isbn, author_name=author_name)
        return jsonify(code=200, message="Book has been successfully added to database")

    except ValueError as e:
        message = str(e)
        return json.dumps({"error": message}), 400


@app.route("/delete", methods=["DELETE"])
def delete():
    try:
        id = request.args.get("id")
        book_data_base.delete_book(id)
        return jsonify(code=200, message="book successfully deleted from database")
    except ValueError as e:
        message = str(e)
        return json.dumps({"error": message}), 400


if __name__ == '__main__':
    app.run(debug=True)
