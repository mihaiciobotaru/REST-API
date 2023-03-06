import random
import sqlite3
from datetime import datetime, timedelta


class Database:
    ERROR = -1
    _connected = False

    def build_response(self):
        rows = self._cursor.fetchall()
        results = []
        for row in rows:
            result = {}
            for column in self._cursor.description:
                result[column[0]] = row[column[0]]
            results.append(result)
        if not results:
            return None
        if results.__len__() == 1:
            return results[0]
        return results

    def __init__(self):
        self._connection = sqlite3.connect('../database.db')
        self._connection.row_factory = sqlite3.Row
        self._cursor = self._connection.cursor()

        result = self.table_exists("users")
        if result == self.ERROR:
            print("[-] Error connecting to database")
            return

        if not result:
            if self.create_users_table() == self.ERROR:
                print("[-] Error creating users table")
                return
            if self.populate_users_table() == self.ERROR:
                print("[-] Error populating users table")
                return

        result = self.table_exists("downloads")
        if result == self.ERROR:
            print("[-] Error connecting to database")
            return

        if not result:
            if self.create_downloads_table() == self.ERROR:
                print("[-] Error creating downloads table")
                return
            if self.populate_downloads_table() == self.ERROR:
                print("[-] Error populating downloads table")
                return

        self._connected = True
        print("[+] Database connected")

    def is_connected(self):
        return self._connected

    def table_exists(self, table_name):
        try:
            self._cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            return self._cursor.fetchone() is not None
        except sqlite3:
            return self.ERROR

    def create_users_table(self):
        try:
            self._cursor.execute(
                'CREATE TABLE users ('
                'id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, age INTEGER, country TEXT, downloads INTEGER,'
                'subscription TEXT DEFAULT "free", last_visit DATETIME, created_at DATETIME, updated_at DATETIME)')
            self._connection.commit()
        except sqlite3:
            return self.ERROR

    def create_downloads_table(self):
        try:
            self._cursor.execute(
                'CREATE TABLE downloads ('
                'id INTEGER PRIMARY KEY, user_id INTEGER, file_name TEXT,'
                'downloaded_at DATETIME)')
            self._connection.commit()
        except sqlite3:
            return self.ERROR

    def populate_users_table(self):
        first_name_list = ['Emily', 'Liam', 'Sophia', 'Noah', 'Emma', 'Ethan', 'Isabella', 'Mason', 'Ava',
                           'Lucas', 'Mia', 'Jacob', 'Charlotte', 'Daniel', 'Lily']
        last_name_list = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Miller', 'Davis', 'Garcia', 'Rodriguez',
                          'Wilson', 'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Hernandez']
        country_list = ['United States', 'United Kingdom', 'Canada', 'Australia', 'New Zealand', 'Ireland', 'Germany']
        subscription_list = ['free', 'lite', 'plus', 'pro']
        for i in range(500):
            first_name = random.choice(first_name_list)
            last_name = random.choice(last_name_list)
            country = random.choice(country_list)
            subscription = random.choice(subscription_list)
            age = random.randint(18, 50)
            downloads = random.randint(0, 1000)

            last_visit = datetime.now() - timedelta(days=random.randint(1, 60))
            created_at = datetime.now() - timedelta(days=random.randint(61, 120))
            updated_at = created_at

            try:
                self._cursor.execute(
                    'INSERT INTO users (first_name, last_name, age, country, downloads, subscription, last_visit, '
                    'created_at, updated_at) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (first_name, last_name, age, country, downloads, subscription, last_visit, created_at, updated_at))
                self._connection.commit()
            except sqlite3:
                return self.ERROR

    def populate_downloads_table(self):
        for i in range(random.randint(100, 1000)):
            user_id = random.randint(1, 500)
            file_name = "video" + str(random.randint(0, random.randint(100, 1000))) + ".mp4"
            downloaded_at = datetime.now() - timedelta(days=random.randint(1, 100))

            try:
                self._cursor.execute(
                    'INSERT INTO downloads (user_id, file_name, downloaded_at) VALUES (?, ?, ?)',
                    (user_id, file_name, downloaded_at))
                self._connection.commit()
            except sqlite3:
                return self.ERROR

    def clean_database(self):
        try:
            self._cursor.execute('DROP TABLE users')
            self._cursor.execute('DROP TABLE downloads')
            self._connection.commit()
            print('[+] Database cleaned')
        except sqlite3:
            return self.ERROR

    def create_user(self, first_name, last_name, age, country):
        downloads = 0
        subscription = 'free'
        last_visit = datetime.now()
        created_at = datetime.now()
        updated_at = datetime.now()

        try:
            self._cursor.execute(
                'INSERT INTO users (first_name, last_name, age, country, downloads, subscription, last_visit, '
                'created_at, updated_at) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (first_name, last_name, age, country, downloads, subscription, last_visit, created_at, updated_at))
            self._connection.commit()

            return self.get_user(self._cursor.lastrowid)
        except sqlite3:
            return self.ERROR

    def create_download(self, user_id, file_name):
        downloaded_at = datetime.now()
        try:
            self._cursor.execute(
                'INSERT INTO downloads (user_id, file_name, downloaded_at) VALUES (?, ?, ?)',
                (user_id, file_name, downloaded_at))
            self._connection.commit()
            return self.get_download(self._cursor.lastrowid)
        except sqlite3:
            return self.ERROR

    def update_user_downloads(self, user_id, downloads):
        try:
            if self.get_user(user_id) is None:
                return None
            self._cursor.execute(
                'UPDATE users SET downloads = ? WHERE id = ?', (downloads, user_id))
            self.update_user_last_visit(user_id, datetime.now())
            self._connection.commit()
            return self.get_user(user_id)
        except sqlite3:
            return self.ERROR

    def update_user_subscription(self, user_id, subscription):
        try:
            if self.get_user(user_id) is None:
                return None
            self._cursor.execute(
                'UPDATE users SET subscription = ? WHERE id = ?', (subscription, user_id))
            self._connection.commit()
            return self.get_user(user_id)
        except sqlite3:
            return self.ERROR

    def update_user_last_visit(self, user_id, last_visit):
        try:
            if self.get_user(user_id) is None:
                return None
            self._cursor.execute(
                'UPDATE users SET last_visit = ? WHERE id = ?', (last_visit, user_id))
            self._connection.commit()
            return self.get_user(user_id)
        except sqlite3:
            return self.ERROR

    def get_users(self):
        try:
            self._cursor.execute('SELECT * FROM users')
            return self.build_response()
        except sqlite3:
            return self.ERROR

    def get_user(self, user_id):
        try:
            self._cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            return self.build_response()
        except sqlite3:
            return self.ERROR

    def get_all_downloads(self):
        try:
            self._cursor.execute('SELECT * FROM downloads')
            return self.build_response()
        except sqlite3:
            return self.ERROR

    def get_user_downloads(self, user_id):
        try:
            self._cursor.execute('SELECT * FROM downloads WHERE user_id = ?', (user_id,))
            return self.build_response()
        except sqlite3:
            return self.ERROR

    def get_download(self, download_id):
        try:
            self._cursor.execute('SELECT * FROM downloads WHERE id = ?', (download_id,))
            return self.build_response()
        except sqlite3:
            return self.ERROR

    def get_user_subscription(self, user_id):
        try:
            self._cursor.execute('SELECT subscription FROM users WHERE id = ?', (user_id,))
            return self.get_user(self._cursor.lastrowid)
        except sqlite3:
            return self.ERROR

    def delete_user(self, user_id):
        try:
            if self.get_user(user_id) is None:
                return None
            self._cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            self._connection.commit()
            return {"DELETED": True}
        except sqlite3:
            return self.ERROR

    def delete_download(self, download_id):
        try:
            if self.get_download(download_id) is None:
                return None
            self._cursor.execute('DELETE FROM downloads WHERE id = ?', (download_id,))
            self._connection.commit()
            return {"DELETED": True}
        except sqlite3:
            return self.ERROR

    def __del__(self):
        self._connection.close()
        print('[+] Database connection closed')

    def close(self):
        self._connection.close()
        print('[+] Database connection closed')
        del self


if __name__ == '__main__':
    db = Database()
    db.clean_database()
