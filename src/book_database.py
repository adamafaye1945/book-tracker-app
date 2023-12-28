import pymysql
from dotenv import load_dotenv
import os


class DatabaseConnection:

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

    def _executor(self, sql_query):
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()
        return results

    def select_column(self, column_name):
        """Return the given column"""
        sql_query = f"SELECT {column_name} FROM books_data"
        return self._executor(sql_query)

    def select_all_row_database(self):
        sql_query = "SELECT * FROM books_data"
        return self._executor(sql_query)

    def select_single_row(self, id):
        """give row knowing id"""
        sql_query = f"SELECT * FROM books_data WHERE id = {id}"
        return self._executor(sql_query)

    def add_book_in(self, isbn, author_name, book_name):
        sql_query = f"INSERT INTO books_data(author_name, ISBN, book_name) VALUES(%s, %s, %s)"
        val = (author_name, isbn, book_name)
        self.cursor.execute(sql_query, val)
        self.conn.commit()
    def delete_book (self,id):
        sql_query = "DELETE FROM books_data WHERE id = %s"
        self.cursor.execute(sql_query, (id))
        self.conn.commit()
