from app.databases.SQLiteProcessor import SQLiteProcessor
from app.collector.CollectorCache import CollectorCache
from app.collector.Display import Display
import json
import pika


class MainProcessor:

    def __init__(self, database_location):
        #   set SQLite processor
        self.sqlite_processor = SQLiteProcessor(database_location=database_location, run_setup=True)

        #   set cache
        self.cache = CollectorCache()

        #   set display
        self.display = Display()

    def is_mac_and_location_in_cache(self, received_data):
        cache_key = "%s_%s_%s" % (received_data.get('mac_address'), received_data.get('latitude'), received_data.get('longitude'))
        if self.cache.is_in_cache(cache_key):
            return True
        else:
            self.cache.add_to_cache(cache_key, 6000)
            return False

    def process(self, received_data):
        if self.is_mac_and_location_in_cache(received_data):
            return

        self.sqlite_processor.insert_into_sqlite(received_data)

        if received_data.get('vendor') is None:
            return

        self.display.set_message(received_data.get('vendor'), received_data.get('mac_address').replace(":", " ")[9:].upper())


if __name__ == '__main__':
    #   set processor
    main_processor = MainProcessor(database_location='/home/pi/tama.db')

    #   set consumer
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='there_and_mac_again')

    #   set callback
    def callback(ch, method, properties, body):
        received_data = json.loads(body)
        main_processor.process(received_data)

    #   start listening
    channel.basic_consume(queue='there_and_mac_again', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()