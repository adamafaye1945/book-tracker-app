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
        # self.users_table = "users"
        # self.userbooks_table = "userbooks"
        # self.book_table = "books_data"

    def _executor(self, sql_query, val):
        self.cursor.execute(sql_query, val)
        results = self.cursor.fetchall()
        if results:
            return results[0]
        return None

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

    def add_book_in_book_data(self, bookId, author_name, book_name, image_url, averageRating):
        sql_query = f"INSERT INTO books_data(bookId, authors, book_name,imageURL, averageRating) VALUES(%s, %s, %s, %s, %s)"
        val = (bookId, author_name, book_name, image_url, averageRating)
        self.cursor.execute(sql_query, val)
        self.conn.commit()



    def delete_book(self, id):
        sql_query = "DELETE FROM books_data WHERE bookId = %s"
        self.cursor.execute(sql_query, (id))
        self.conn.commit()

    def add_users(self, id, email,name,  password):
        sql_query = "INSERT INTO userLogin(UserID, Email,name,password) VALUES( %s,%s, %s,%s)"
        # encrypting
        password = bcrypt.hashpw(password=password.encode("utf-8"), salt=bcrypt.gensalt())
        val = (id, email,name, password)
        self.cursor.execute(sql_query, val)
        self.conn.commit()

    def authenticate(self, email, password):
        # encrypting
        sql_query = "SELECT name, password, UserID FROM userLogin WHERE email = %s"
        val = email
        result = self._executor(sql_query, val)
        if result:
            hashed_password = result[0]
            if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
                return result[1]
        return None
