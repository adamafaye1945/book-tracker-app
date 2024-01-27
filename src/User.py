from flask_login import UserMixin
from book_database import DatabaseConnection


class User(UserMixin):
    def __init__(self, userID, email, hashed_password, name):
        self.userID = userID
        self.email = email
        self.name = name
        self.password = hashed_password
