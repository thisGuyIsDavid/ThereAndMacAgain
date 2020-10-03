import json

import pika
import time
from pika.exceptions import AMQPConnectionError
from app.collector.GPSCollector import GPSCollector
from app.collector.Keypad import Keypad
from app.collector.StatusLights import StatusLights
from app.collector.WIFICollector import WIFICollector


class MainCollector:

    def __init__(self, gps_port, wifi_port):

        self.gps_collector = GPSCollector(gps_port)
        self.gps_collector.setup()

        self.wifi_collector = WIFICollector(wifi_port)
        self.wifi_collector.setup()

        #   Status Lights
        self.status_lights = StatusLights()

        #   set message queue
        self.message_queue_connection = None
        self.message_queue = None
        self.set_messaging_queue()

        #   Keypad
        self.keypad = Keypad()

    def set_messaging_queue(self):
        #   Messaging Queue - try setting 30 times.
        self.status_lights.set_program_status(-1)
        for i in range(30):
            try:
                self.message_queue_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                self.message_queue = self.message_queue_connection.channel()
                self.message_queue.queue_declare(queue='there_and_mac_again')
                self.status_lights.set_misc_status(1)
                break
            except AMQPConnectionError:
                print('connection error')
                time.sleep(5)

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

                self.status_lights.set_process_status(1)
                self.message_queue.basic_publish(exchange='', routing_key='there_and_mac_again', body=json.dumps(collected_data))
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
            self.status_lights.clear()
            self.message_queue_connection.close()

if __name__ == '__main__':
    MainCollector(wifi_port='/dev/ttyUSB1', gps_port='/dev/ttyUSB0').run()