#!/usr/bin/env python
from app.databases.SQLiteProcessor import SQLiteProcessor
from app.collector.CollectorCache import CollectorCache
from app.collector.Display import Display


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
        mac_address = received_data.get('mac_address')
        if self.is_mac_and_location_in_cache(received_data):
            return

        print(mac_address)

        if received_data.get('vendor') is None:
            return

        self.display.set_message(
            received_data.get('vendor'),
            received_data.get('mac_address').replace(":", " ")[9:].upper()
        )
        self.sqlite_processor.insert_into_sqlite(received_data)
