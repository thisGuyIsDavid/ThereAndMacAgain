# !/usr/bin/env python
import time
import serial

from app.RedisCache import RedisCache
from app.SQLiteProcessor import SQLiteProcessor
from rpi_ws281x import PixelStrip, Color


class WiFiDeviceReader:
	PROGRAM_LIGHT_POS = 0
	GPS_LIGHT_POS = 1
	WIFI_LIGHT_POS = 2

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

		# set status lights
		self.status_light = PixelStrip(8, 18, 800000, 10, False, 100, 0)
		self.status_light.begin()

		for pin in [self.PROGRAM_LIGHT_POS, self.GPS_LIGHT_POS, self.WIFI_LIGHT_POS]:
			self.set_light(pin,  Color(255, 0, 0))


	def set_light(self, pin, color):
		self.status_light.setPixelColor(pin, color)
		self.status_light.show()

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
		if self.redis_cache.is_key_in_store(wifi_data.get('mac_address')):
			return
		else:
			self.redis_cache.set_key(wifi_data.get('mac_address'), 1, 180)

		# set WiFi data
		self.wifi_data = wifi_data

	@staticmethod
	def process_wifi_data(wifi_data):
		wifi_array = wifi_data.strip().replace("\n", "").split('|')
		return {
			"mac_address": wifi_array[0],
			"name": wifi_array[1]
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
			self.redis_cache.set_key(key_name, 1, 3600)
		self.sqlite_processor.insert_into_sqlite(cleaned_data)
		self.number_collected += 1

	def process_serial_input(self):
		while True:
			try:
				self.set_light(self.PROGRAM_LIGHT_POS, Color(0, 255, 0))

				self.set_gps_data()
				if self.gps_data is None:
					self.set_light(self.GPS_LIGHT_POS, Color(0, 255, 255))
					continue
				self.set_light(self.GPS_LIGHT_POS, Color(0, 255, 0))

				self.set_wifi_data()
				if self.wifi_data is None:
					self.set_light(self.WIFI_LIGHT_POS, Color(0, 0, 255))
					continue
				self.set_light(self.WIFI_LIGHT_POS, Color(0, 255, 0))

				self.process_collected_data()

			except Exception as e:
				with open('errorlog.txt', 'a') as error_log:
					error_log.write(str(e) + '\n')
					self.set_light(self.PROGRAM_LIGHT_POS, Color(0, 0, 255))

				continue

	def run(self):
		try:
			self.process_serial_input()
		except KeyboardInterrupt as ki:
			pass
		except Exception as e:
			with open('errorlog.txt', 'a') as error_log:
				error_log.write(str(e))
		finally:
			self.set_light(self.PROGRAM_LIGHT_POS, Color(255, 0, 0))
			self.sqlite_processor.close_connection()

