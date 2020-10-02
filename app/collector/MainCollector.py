from app.collector.GPSCollector import GPSCollector
from app.collector.WIFICollector import WIFICollector
from app.databases.SQLiteProcessor import SQLiteProcessor
from app.collector.StatusLights import StatusLights
from app.collector.CollectorCache import CollectorCache
from app.collector.Display import Display
from app.collector.Keypad import Keypad
import pika
import json


class MainCollector:

    def __init__(self, gps_port, wifi_port, database_location):

        self.gps_collector = GPSCollector(gps_port)
        self.gps_collector.setup()

        self.wifi_collector = WIFICollector(wifi_port)
        self.wifi_collector.setup()

        self.cache = CollectorCache()

        #   set message queue
        self.message_queue_connection = None
        self.message_queue = None
        self.set_messaging_queue()

        # set SQLite processor
        self.sqlite_processor = SQLiteProcessor(database_location=database_location, run_setup=True)

        #   Status Lights
        self.status_lights = StatusLights()

        #   Keypad
        self.keypad = Keypad()

        self.display = Display()

    def set_messaging_queue(self):
        #   Messaging Queue
        self.message_queue_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.message_queue = self.message_queue_connection.channel()
        self.message_queue.queue_declare(queue='there_and_mac_again')

    def is_in_mac_address_cache(self, mac_address):
        # check cache. This is for when the device is in motion.
        if self.cache.is_in_cache(mac_address):
            return True
        else:
            self.cache.add_to_cache(mac_address, 30)
            return False

    def is_mac_and_location_in_cache(self, mac_address, latitude, longitude):
        key_name = "%s_%s_%s" % (mac_address, latitude, longitude)
        if self.cache.is_in_cache(key_name):
            return True
        else:
            self.cache.add_to_cache(key_name, 6000)
            return False

    def process_collected_data(self, collected_data):
        #   if there is no keypad press, do standard caching.
        if collected_data.get('key_value') is None:
            if self.is_in_mac_address_cache(collected_data.get('mac_address')):
                return
            if self.is_mac_and_location_in_cache(collected_data.get('mac_address'), collected_data.get('latitude'), collected_data.get('longitude')):
                return

        self.status_lights.set_process_status(1)

        self.message_queue.basic_publish(exchange='', routing_key='there_and_mac_again', body=json.dumps(collected_data))
        if collected_data.get('vendor') is None:
            return

        self.display.set_message(
            collected_data.get('vendor'),
            collected_data.get('mac_address').replace(":", " ")[9:].upper()
        )

    def read_collectors(self):
        self.status_lights.set_program_status(1)
        while True:
            try:
                pressed_key = self.keypad.get_key_value()

                #   reset process light
                self.status_lights.set_process_status(0)

                gps_data = self.gps_collector.get_line()
                if gps_data is None:
                    self.status_lights.set_gps_status(-1)
                    continue
                self.status_lights.set_gps_status(1)

                wifi_data = self.wifi_collector.get_line()
                if wifi_data is None:
                    self.status_lights.set_wifi_status(-1)
                    continue
                self.status_lights.set_wifi_status(1)

                collected_data = {**gps_data, **wifi_data}
                collected_data['key_value'] = pressed_key

                self.process_collected_data(collected_data)
            except Exception as e:
                print(e)
                continue

    def run(self):
        try:
            self.read_collectors()
        except KeyboardInterrupt as ki:
            pass
        except Exception as e:
            with open('errorlog.txt', 'a') as error_log:
                error_log.write(str(e))
        finally:
            self.display.clear()
            self.status_lights.clear()
            self.message_queue_connection.close()
            pass