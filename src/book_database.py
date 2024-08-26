import pymysql
from dotenv import load_dotenv
import os
import bcrypt


class DatabaseConnection:
    """This class contains all the tables of the database. Equipped with functions that are capable of running SQL
    queries to add, retrieve, delete data from our databases."""

    def __init__(self) -> None:
        load_dotenv()
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'db': os.getenv('DB_NAME')
        }
        self.conn = pymysql.connect(**self.db_config)
        self.cursor = self.conn.cursor()
        self.salt = bcrypt.gensalt()

    def execute_commit(self, sql_query, val):
        self._ensure_database_connection()
        self.cursor.execute(sql_query, val)
        self.conn.commit()

    def execute_query(self, sql_query, val=None):
        self._ensure_database_connection()
        self.cursor.execute(sql_query, val)
        results = self.cursor.fetchall()
        if results:
            return results
        return None

    def check_duplicate_book(self, book_id):
        """Check duplicate entry for books_data"""
        sql_query = "SELECT 1 FROM books_data WHERE bookId = %s LIMIT 1"
        results = self.execute_query(sql_query, (book_id,))
        return bool(results)

    def _ensure_database_connection(self):
        try:
            self.conn.ping(reconnect=True)
        except pymysql.MySQLError:
            self.conn = pymysql.connect(**self.db_config)
            self.cursor = self.conn.cursor()

    def select_column_from_table(self, column_name, table):
        """Return the given column from a specified table"""
        sql_query = f"SELECT {column_name} FROM {table}"
        return self.execute_query(sql_query)

    def select_all_rows_from_table(self, table):
        sql_query = f"SELECT * FROM {table}"
        return self.execute_query(sql_query)

    def select_single_row_from_table(self, book_id, table):
        """Get a row by bookId"""
        sql_query = f"SELECT * FROM {table} WHERE bookId = %s"
        return self.execute_query(sql_query, (book_id,))

    def get_books(self, user_id):
        # Getting bookIds added by the user
        sql_query = "SELECT bookId, reflection, rating FROM userAction WHERE userId = %s"
        result = self.execute_query(sql_query, (user_id,))
        data_bulk = []
        if not result:
            return data_bulk
        for query_result in result:
            data = self.select_single_row_from_table(book_id=query_result[0], table="books_data")
            if data:
                json_data = {
                    "bookId": data[0][0],
                    "authors": data[0][1],
                    "title": data[0][2],
                    "imageUrl": data[0][3],
                    "averageRating": data[0][4],
                    "tracked": True,
                    "publisher": data[0][5],
                    "reflection": query_result[1],
                    "userRating": query_result[2],
                    "reviewed": True if query_result[1] != "" and query_result[2] != 0 else False
                }
                data_bulk.append(json_data)
        return data_bulk

    def add_book_to_data(self, book_id, author_name, book_name, image_url, average_rating, publisher):
        if self.check_duplicate_book(book_id):
            return
        sql_query = (
            "INSERT INTO books_data(bookId, authors, book_name, imageURL, averageRating, publisher) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        val = (book_id, author_name, book_name, image_url, average_rating, publisher)
        self.execute_commit(sql_query, val)

    def add_or_update_reflection_and_rating(self, user_id, reflection, rating, book_id):
        # Checking if there is a duplicate
        sql_query_check = "SELECT COUNT(*) FROM userAction WHERE userId = %s AND bookId = %s"
        val_check = (user_id, book_id)
        if self.execute_query(sql_query_check, val_check)[0][0] > 0:  # Reflection already exists; we update
            sql_query = "UPDATE userAction SET reflection = %s, rating = %s WHERE bookId = %s AND userId = %s"
            val = (reflection, rating, book_id, user_id)
        else:
            sql_query = "INSERT INTO userAction (userId, bookId, reflection, rating) VALUES (%s, %s, %s, %s)"
            val = (user_id, book_id, reflection, rating)

        self.execute_commit(sql_query, val)

    def delete_book(self, book_id):
        sql_query = "DELETE FROM userAction WHERE bookId = %s"
        self.execute_commit(sql_query, (book_id,))

    def add_user(self, email, name, password):
        sql_query = "INSERT INTO userLogin (Email, password, name) VALUES (%s, %s, %s)"
        # Encrypting the password
        hashed_password = bcrypt.hashpw(password=password.encode("utf-8"), salt=bcrypt.gensalt())
        val = (email, hashed_password.decode('utf-8'), name)
        self.execute_commit(sql_query, val)

    def authenticate(self, email, password):
        # Return user info if password and email are correct
        sql_query = "SELECT * FROM userLogin WHERE email = %s"
        result = self.execute_query(sql_query, (email,))
        if result:
            hashed_password = result[0][2]
            if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
                return result[0]
        return None

    def retrieve_user(self, email=None, name=None, user_id=None):
        if name:
            sql_query = "SELECT userId, name FROM userLogin WHERE name LIKE %s"
            users = self.execute_query(sql_query, ("%" + name + "%",))
            return users
        if user_id:
            sql_query = "SELECT userId FROM userLogin WHERE userId = %s"
            user = self.execute_query(sql_query, (user_id,))
            if user:
                return user[0]
            return None

        sql_query = "SELECT * FROM userLogin WHERE email = %s"
        user = self.execute_query(sql_query, (email,))
        if user:
            return user[0]
        return None

    def create_friendship(self, user_id, new_friend_id):
        # Check if the user is already in the friendship list and avoid adding duplicates or adding oneself
        if user_id == new_friend_id:
            return False

        query = "SELECT friend1 FROM friendship WHERE friend1 = %s"
        id_exist = self.execute_query(query, (user_id,))

        if id_exist:
            sql_query = "UPDATE friendship SET userFriend = JSON_ARRAY_APPEND(userFriend, '$', %s) WHERE friend1 = %s"
            val = (new_friend_id, user_id)
        else:
            sql_query = "INSERT INTO friendship (friend1, userFriend) VALUES (%s, JSON_ARRAY(%s))"
            val = (user_id, new_friend_id)

        self.execute_commit(sql_query, val)
        return True

    def end_friendship(self, user_id, friend_id):
        # Remove a friend from the user's friendship list
        sql_query = "UPDATE friendship SET userFriend = JSON_REMOVE(userFriend, JSON_UNQUOTE(JSON_SEARCH(userFriend, 'one', %s))) WHERE friend1 = %s"
        val = (friend_id, user_id)
        self.execute_commit(sql_query, val)
