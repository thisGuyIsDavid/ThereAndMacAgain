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
			cursor.execute("CREATE TABLE mac_data(id INTEGER PRIMARY KEY AUTOINCREMENT, mac_address TEXT, name TEXT, latitude TEXT, longitude TEXT, timestamp TEXT);")
		self.database_connection.commit()

	def insert_into_sqlite(self, message_dictionary):
		cursor = self.database_connection.cursor()
		cursor.execute(
			"""
			INSERT INTO mac_data (
				mac_address, name, latitude, longitude, timestamp
			) VALUES (
				'%s', '%s', '%s', '%s', '%s'
			)
			""" % (message_dictionary.get('mac_address'), message_dictionary.get('name'), message_dictionary.get('latitude'), message_dictionary.get('longitude'), message_dictionary.get('timestamp'))
		)
		cursor.close()
		self.database_connection.commit()

	def close_connection(self):
		self.database_connection.close()

	def get_data(self):
		cursor = self.database_connection.cursor()
		cursor.execute("SELECT mac_address, name, latitude, longitude, timestamp FROM mac_data")
		results = cursor.fetchall()
		cursor.close()

		return [
			{
				"mac_address": result[0].replace(":", "").upper(),
				"latitude": result[1],
				"longitude": result[2],
				"when_recorded": result[3]
			} for result in results
		]

if __name__ == '__main__':
    print(len(SQLiteProcessor('/Users/davidhaverberg/PycharmProjects/ThereAndMacAgain/data.db').get_data()))