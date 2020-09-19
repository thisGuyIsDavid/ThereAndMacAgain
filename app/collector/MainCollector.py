from app.collector.GPSCollector import GPSCollector
from app.collector.WIFICollector import WIFICollector


class MainCollector:

    def __init__(self, gps_port, wifi_port, database_location):

        self.gps_collector = GPSCollector(gps_port)
        self.gps_collector.set_collector()

        self.wifi_collector = WIFICollector(wifi_port)
        self.wifi_collector.set_collector()

    def read_collectors(self):
        while True:
            try:
                gps_data = self.gps_collector.get_line()
                if gps_data is None:
                    continue

                wifi_data = self.wifi_collector.get_line()
                if wifi_data is None:
                    continue

                print(gps_data, wifi_data)

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