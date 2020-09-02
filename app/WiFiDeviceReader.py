# !/usr/bin/env python
from app.displays.TMBoards import TMBoards
import serial

from app.SQLiteProcessor import SQLiteProcessor
from app.RedisCache import RedisCache
import time


class WiFiDeviceReader:

	number_collected = 0
	when_started = time.time()

	gps_serial_reader = None
	gps_data = None

	wifi_serial_reader = None
	wifi_data = None

	def __init__(self, wifi_serial_port, gps_serial_port, database_location):
		# set display
		self.tm_board = TMBoards(19, 13, 6, 1)

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
		self.tm_board.leds[2] = True

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

		# check cache
		if self.redis_cache.is_key_in_store(key_name):
			return
		else:
			self.redis_cache.set_key(key_name, 1, 600)

		self.tm_board.leds[3] = True
		self.sqlite_processor.insert_into_sqlite(cleaned_data)
		self.number_collected += 1

	def process_serial_input(self):
		while True:
			# GPS
			self.tm_board.leds[1] = False

			# Wifi
			self.tm_board.leds[2] = False

			# General
			self.tm_board.leds[3] = False

			try:
				self.set_gps_data()
				if self.gps_data is None:
					continue
				self.tm_board.leds[1] = True

				self.set_wifi_data()
				if self.wifi_data is None:
					continue
				self.tm_board.leds[2] = True

				self.process_collected_data()

				self.display_count()
			except Exception as e:
				print(e)
				continue

	def display_count(self):
		number_collected_string = str(self.number_collected)
		if len(number_collected_string) > 4:
			self.tm_board.segments[0] = '9999'
		else:
			self.tm_board.segments[0] = "%s%s" % ("0" * (4 - len(str(self.number_collected))), self.number_collected)

		seconds_since_start = round(time.time() - self.when_started)
		average = self.number_collected / seconds_since_start
		if average < 1:
			average = round(average, 3)
		else:
			average = round(average, 1)


		print(str(average))

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

