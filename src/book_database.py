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
        sql_query = f"SELECT * FROM {table} WHERE id = %s "
        val = id
        return self._executor(sql_query, val)

    def add_book_in_table(self, isbn, author_name, book_name):
        sql_query = f"INSERT INTO books_data(author_name, ISBN, book_name) VALUES(%s, %s, %s)"
        val = (author_name, isbn, book_name)
        self.cursor.execute(sql_query, val)
        self.conn.commit()

    def delete_book(self, id):
        sql_query = "DELETE FROM books_data WHERE id = %s"
        self.cursor.execute(sql_query, (id))
        self.conn.commit()

    def add_users(self, id, email, password):
        sql_query = "INSERT INTO users(UserID, Email, password) VALUES( %s, %s,%s)"
        # encrypting
        password = bcrypt.hashpw(password=password)
        val = (id, email, password)
        self.cursor.execute(sql_query, val)
        self.conn.commit()

    def authenticate(self, email, password):
        # encrypting
        password = bcrypt.hashpw(password=password)
        sql_query = "SELECT UserID FROM users WHERE email = %s AND password = %s"
        val = (email, password)
        return self._executor(sql_query, val)
