import pymysql
from dotenv import load_dotenv
import os
import bcrypt


class DatabaseConnection:
    """This class contains all the table of the database. Equipped with function that are capable of running SQL
    queries to add, retrieve, delete data from our databases"""

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


    def _executor(self, sql_query, val):
        self._ensure_database_connection()
        self.cursor.execute(sql_query, val)
        results = self.cursor.fetchall()
        if results:
            return results[0]
        return None

    def _duplicate_checker(self, id):
        """check duplicate entry for books_data"""
        sql_query = "SELECT * FROM books_data WHERE bookId = %s"
        if self._executor(sql_query, id):
            return True
        return False

    def _ensure_database_connection(self):
        try:
            self.conn.ping(reconnect=True)
        except pymysql.err:
            self.conn.connect()

    def select_column_table(self, column_name, table):
        """Return the given column"""
        sql_query = f"SELECT %s FROM %s"
        val = (column_name, table)
        return self._executor(sql_query, val)

    def select_all_row_table(self, table):
        sql_query = "SELECT * FROM %s"
        return self._executor(sql_query, table)

    def select_single_row_table(self, id, table):
        """give row knowing id"""
        sql_query = f"SELECT * FROM {table} WHERE bookId = %s "
        val = id
        return self._executor(sql_query, val)
    def get_books(self, id):
        # getting bookids added by the user
        sql_query_for_bookid = "SELECT bookId FROM userAction WHERE userId = %s"
        self.cursor.execute(sql_query_for_bookid, id)
        result = self.cursor.fetchall()
        #cleaning
        book_ids = [element[0] for element in result]
        data_bulk = []
        for bookid in book_ids:
            data = self.select_single_row_table(bookid, "books_data")
            json_data = {
                "bookId": data[0],
                "authors": data[1],
                "book_name":data[2],
                "image_url":data[3],
                "averageRating":data[4],
            }
            data_bulk.append(json_data)
        return data_bulk

    def add_book_in_book_data(self, bookId, author_name, book_name, image_url, averageRating):
        if self._duplicate_checker(bookId):
            return
        sql_query = (f"INSERT INTO books_data(bookId, authors, book_name,imageURL, averageRating) VALUES( %s, %s, %s, "
                     f"%s, %s)")
        val = (bookId, author_name, book_name, image_url, averageRating)
        self._ensure_database_connection()
        self.cursor.execute(sql_query, val)
        self.conn.commit()
    def adding_reflection_and_rating(self, user_id, reflection, rating, bookID):
        # checking if there is a duplicate
        sql_query_check = "SELECT COUNT(*) FROM userAction WHERE userId = %s AND bookId = %s"
        val_check = (user_id, bookID)
        if int(self._executor(sql_query_check, val_check)[0]) > 0:
            return
        sql_query = "INSERT INTO userAction (userId, bookId, reflection, rating) VALUES (%s, %s, %s, %s)"
        val = (user_id, bookID, reflection, rating)
        self._ensure_database_connection()
        self.cursor.execute(sql_query, val)
        self.conn.commit()

    def delete_book(self, id):
        sql_query = "DELETE FROM books_data WHERE bookID = %s"
        self.cursor.execute(sql_query, id)
        self.conn.commit()

    def add_users(self, email, name, password):
        sql_query = "INSERT INTO userLogin(Email,password,name) VALUES( %s, %s,%s)"
        # encrypting
        password = bcrypt.hashpw(password=password.encode("utf-8"), salt=bcrypt.gensalt())
        val = (email, password, name)
        self.cursor.execute(sql_query, val)
        self.conn.commit()

    def authenticate(self, email, password):
        # return user info if password and email is correct
        sql_query = "SELECT * FROM userLogin WHERE email = %s"
        val = email
        result = self._executor(sql_query, val)
        if result:
            hashed_password = result[2]
            if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
                return result
        return None

    def retrieve_user(self, id):
        sql_query = "SELECT * from userLogin WHERE userID = %s"
        user = self._executor(sql_query, id)
        if user:
            return user
        return None
