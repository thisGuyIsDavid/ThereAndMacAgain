from app.collector.GPSCollector import GPSCollector
from app.collector.WIFICollector import WIFICollector
from app.databases.RedisCache import RedisCache
from app.databases.SQLiteProcessor import SQLiteProcessor


class MainCollector:

    def __init__(self, gps_port, wifi_port, database_location):

        self.gps_collector = GPSCollector(gps_port)
        self.gps_collector.setup()

        self.wifi_collector = WIFICollector(wifi_port)
        self.wifi_collector.setup()

        self.redis_cache = RedisCache()

        # set SQLite processor
        self.sqlite_processor = SQLiteProcessor(database_location=database_location, run_setup=True)

    def is_in_mac_address_cache(self, mac_address):
        # check cache. This is for when the device is in motion.
        if self.redis_cache.is_key_in_store(mac_address):
            return True
        else:
            self.redis_cache.set_key(mac_address, 1, 30)
            return False

    def is_mac_and_location_in_cache(self, mac_address, latitude, longitude):
        key_name = "%s_%s_%s" % (mac_address, latitude, longitude)
        if self.redis_cache.is_key_in_store(key_name):
            return True
        else:
            self.redis_cache.set_key(key_name, 1, 6000)
            return False

    def process_collected_data(self, collected_data):

        if self.is_in_mac_address_cache(collected_data.get('mac_address')):
            return
        if self.is_mac_and_location_in_cache(collected_data.get('mac_address'), collected_data.get('latitude'), collected_data.get('longitude')):
            return
        self.sqlite_processor.insert_into_sqlite(collected_data)
        print(collected_data)

    def read_collectors(self):
        while True:
            try:
                gps_data = self.gps_collector.get_line()
                if gps_data is None:
                    continue
                wifi_data = self.wifi_collector.get_line()
                if wifi_data is None:
                    continue
                collected_data = {**gps_data, **wifi_data}

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
           pass