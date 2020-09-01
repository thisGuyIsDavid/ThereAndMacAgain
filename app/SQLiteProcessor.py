import sqlite3
import json
import datetime


class SQLiteProcessor:
	def __init__(self, database_location, run_setup=False):
		self.database_connection = sqlite3.connect(database_location)
		if run_setup:
			self.setup_sqlite()

	def setup_sqlite(self):
		cursor = self.database_connection.cursor()
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mac_data';")
		if len(cursor.fetchall()) == 0:
			cursor.execute("CREATE TABLE mac_data(id INTEGER PRIMARY KEY AUTOINCREMENT, mac_address TEXT, latitude TEXT, longitude TEXT, date_inserted TEXT);")
		self.database_connection.commit()

	def insert_into_sqlite(self, message_dictionary):
		cursor = self.database_connection.cursor()
		cursor.execute("INSERT INTO mac_data (message, date_inserted) VALUES ('%s', '%s')" % (json.dumps(message_dictionary), datetime.datetime.now() ))
		cursor.close()
		self.database_connection.commit()

	def close_connection(self):
		self.database_connection.close()
