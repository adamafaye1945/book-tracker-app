


class User():
    def __init__(self, userID, email, hashed_password, name):
        self.id = userID
        self.email = email
        self.name = name
        self.password = hashed_password