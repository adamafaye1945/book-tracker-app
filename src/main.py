from flask import Flask, jsonify, request
from book_database import DatabaseConnection
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from User import User
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")
jwt = JWTManager(app)
CORS(app)
my_database = DatabaseConnection()


# firebase

cred = credentials.Certificate(os.getenv("FIREBASE_JSON"))
firebase_admin.initialize_app(cred)
db = firestore.client()
def send_message(sender_id, receiver_id, chat_id, message):
    # Store the message in Firestore
    doc_ref = db.collection('chats').document(chat_id).collection('messages').document()
    doc_ref.set({
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'message': message,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    return {"status": "success", "message": "Message sent"}
@app.route("/send_message", methods =["POST"])
def message_route():
    data = request.get_json()
    chat_id = data["chat_id"]
    sender_id = data["sender_id"]
    receiver_id = data["receiver_id"]
    message = data["message"]
    try:
        response = send_message(sender_id=sender_id, receiver_id=receiver_id, message=message, chat_id = chat_id)
    except:
        return jsonify(response="error sending message"), 400

    return jsonify(response = response), 200





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
        return jsonify(book_data=[], response=200), 200
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
            if data.get("untracked", False):
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
                    raise ValueError("Missing book id information, if unknown enter them as 'NULL', also check params")
                my_database.add_book_to_data(
                    book_id=bookId,
                    author_name=author_name,
                    image_url=imageUrl,
                    average_rating=averageRating,
                    book_name=book_name,
                    publisher=publisher
                )
                my_database.add_or_update_reflection_and_rating(
                    user_id=user_id,
                    reflection=user_reflection,
                    book_id=bookId,
                    rating=user_rating
                )
        return jsonify(message="Database was successfully updated"), 200
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
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
            users = my_database.retrieve_user_friend(userid=user.id)
            return jsonify(id=user.id, name=user.name, access_token=access_token,user_friends= users), 200

        raise ValueError("User not found")
    except ValueError:
        return jsonify(message="User not found"), 400


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
        if my_database.retrieve_user(email=email):
            return jsonify(message="User already exists"), 409
        my_database.add_user(password=password, email=email, name=name)
        return jsonify(message="User was successfully added to the database"), 200

    except ValueError as e:
        message = str(e)
        return jsonify(error=message), 400

@app.route("/sendFriendRequest", methods =["POST"])
@jwt_required()
def send_request():
    id = get_jwt_identity()
    try:
        receiver_id = request.args.get("receiverId")
        my_database.create_request(sender_id=id, receiver_id=receiver_id)
        return jsonify(message= "friendRequest sent"), 200

    except:
        return jsonify(message = "error sending request"), 400

def add_friend(friend_id):
    id = get_jwt_identity()
    return my_database.create_friendship(id, friend_id)
@app.route("/acceptRequest", methods = ["POST"])
@jwt_required()
def accept_request():
    try:
        data = request.args.get("requestId")
        sender_id = my_database.get_request_sender_id(data)
        if add_friend(friend_id=sender_id):
            return jsonify(message = "friendship set!"), 200
        raise ValueError("no sender id or no requestId")
    except:
        return jsonify(message ="error setting friendship, check argument or if a request has been made")



@app.route("/find", methods=["GET"])
@jwt_required()
def find_users():
    name = request.args.get("name")
    users = my_database.retrieve_user(name=name)
    if not users:
        return jsonify(message="No user found"), 400
    return_obj = []
    for user in users:
        user_obj = {
            "name": user[1],
            "userid": user[0]
        }
        return_obj.append(user_obj)
    return jsonify(users=return_obj)


if __name__ == '__main__':
    app.run(debug=True)
