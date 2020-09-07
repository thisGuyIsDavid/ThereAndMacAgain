# !/usr/bin/env python
import time

import serial

from app.RedisCache import RedisCache
from app.SQLiteProcessor import SQLiteProcessor


class WiFiDeviceReader:

	number_collected = 0
	when_started = time.time()

	gps_serial_reader = None
	gps_data = None

	wifi_serial_reader = None
	wifi_data = None

	def __init__(self, wifi_serial_port, gps_serial_port, database_location):
		# set serial
		self.set_wifi_serial(wifi_serial_port)
		self.set_gps_serial(gps_serial_port)

		# set cache
		self.redis_cache = RedisCache()

		# set SQLite processor
		self.sqlite_processor = SQLiteProcessor(database_location=database_location, run_setup=True)

	# GPS data
	def set_gps_serial(self, gps_serial_port):
		if gps_serial_port is None:
			return

		self.gps_serial_reader = serial.Serial(
			port=gps_serial_port,
			baudrate=115200,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			timeout=1
		)

	def set_gps_data(self):
		# clear GPS data.
		self.gps_data = None

		# get the string
		gps_message = self.gps_serial_reader.readline()
		gps_message = gps_message.decode('utf-8').strip()
		if gps_message == "":
			return

		# convert to dictionary
		gps_data = self.process_gps_data(gps_message)
		if gps_data is None:
			return

		# check gps connection
		if '*' in gps_data.get('latitude'):
			return

		# set data
		self.gps_data = gps_data

	@staticmethod
	def process_gps_data(gps_data):
		gps_array = [x for x in gps_data.strip().split('|') if x != '']
		latitude = round(float(gps_array[0]), 4)
		longitude = round(float(gps_array[1]), 4)

		return {
			"latitude": str(latitude),
			"longitude": str(longitude),
			"timestamp": gps_array[2]
		}

	# WiFi data
	def set_wifi_serial(self, wifi_serial_port):
		if wifi_serial_port is None:
			return

		self.wifi_serial_reader = serial.Serial(
			port=wifi_serial_port,
			baudrate=115200,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			timeout=1
		)

	def set_wifi_data(self):
		# clear WiFi variable
		self.wifi_data = None

		# get the string
		wifi_message = self.wifi_serial_reader.readline()
		wifi_message = wifi_message.decode('utf-8').strip()
		if wifi_message == "":
			return

		# convert to dictionary
		wifi_data = self.process_wifi_data(wifi_message)
		if wifi_data is None:
			return

		# check cache. This is for when the device is in motion.
		if self.redis_cache.is_key_in_store(wifi_data):
			return
		else:
			self.redis_cache.set_key(wifi_data, 1, 60)

		# set WiFi data
		self.wifi_data = wifi_data

	@staticmethod
	def process_wifi_data(wifi_data):
		wifi_array = wifi_data.strip().replace("\n", "").split('|')
		return {
			"mac_address": wifi_array[0]
		}

	# All data
	def process_collected_data(self):
		collected_data = {**self.gps_data, **self.wifi_data}
		cleaned_data = {key: value if value != '' else None for key, value in collected_data.items()}
		key_name = "%s_%s_%s" % (cleaned_data.get('mac_address'), cleaned_data.get('latitude'), cleaned_data.get('longitude'))

		# check cache. This is for when the device is not in motion.
		if self.redis_cache.is_key_in_store(key_name):
			return
		else:
			self.redis_cache.set_key(key_name, 1, 600)
		print(cleaned_data)

		self.sqlite_processor.insert_into_sqlite(cleaned_data)
		self.number_collected += 1

	def process_serial_input(self):
		while True:
			try:
				self.set_gps_data()
				if self.gps_data is None:
					continue

				self.set_wifi_data()
				if self.wifi_data is None:
					continue

				self.process_collected_data()

			except Exception as e:
				print(e)
				continue

	def run(self):
		try:
			self.process_serial_input()
		except KeyboardInterrupt as ki:
			pass
		except Exception as e:
			print(e)
			with open('errorlog.txt', 'w') as error_log:
				error_log.write(str(e))
		finally:
			self.sqlite_processor.close_connection()

