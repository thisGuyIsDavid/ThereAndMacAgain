import sqlite3


class SQLiteProcessor:
	def __init__(self, database_location, run_setup=False):
		self.database_connection = sqlite3.connect(database_location)
		if run_setup:
			self.setup_sqlite()

	def setup_sqlite(self):
		cursor = self.database_connection.cursor()
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mac_data';")
		if len(cursor.fetchall()) == 0:
			cursor.execute("CREATE TABLE mac_data(id INTEGER PRIMARY KEY AUTOINCREMENT, mac_address TEXT, latitude TEXT, longitude TEXT, timestamp TEXT);")
		self.database_connection.commit()

	def insert_into_sqlite(self, message_dictionary):
		cursor = self.database_connection.cursor()
		cursor.execute(
			"""
			INSERT INTO mac_data (
				mac_address, latitude, longitude, timestamp
			) VALUES (
				'%s', '%s', '%s', '%s'
			)
			""" % (message_dictionary.get('mac_address'), message_dictionary.get('latitude'), message_dictionary.get('longitude'), message_dictionary.get('timestamp'))
		)
		print(message_dictionary)
		cursor.close()
		self.database_connection.commit()

	def close_connection(self):
		self.database_connection.close()

	def get_data(self):
		cursor = self.database_connection.cursor()
		cursor.execute("SELECT * FROM mac_data")
		x = cursor.fetchall()
		cursor.close()
		print(x)

		pass


if __name__ == '__main__':
	SQLiteProcessor('/Users/davidhaverberg/PycharmProjects/ThereAndMacAgain/data.db').get_data()
	pass