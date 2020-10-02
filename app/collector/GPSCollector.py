# !/usr/bin/env python
from app.collector.SerialCollector import SerialCollector
import time


class GPSCollector(SerialCollector):

    latitude = None
    longitude = None
    timestamp = None

    reading_age = None

    def get_coordinates(self, check_age=True):
        if check_age and (self.reading_age is None or time.time() - self.reading_age > 10):
            #   readings older than ten seconds are no counted.
            self.reading_age = None
            return

        return {
            "latitude": str(self.latitude),
            "longitude": str(self.longitude),
            "timestamp": self.timestamp
        }

    def process_line(self, line):
        # check gps connection
        if '*' in line:
            return self.get_coordinates()

        gps_array = [x for x in line.strip().split('|') if x != '']

        try:
            self.latitude = round(float(gps_array[0]), 4)
            self.longitude = round(float(gps_array[1]), 4)
            self.timestamp = gps_array[2]
            self.reading_age = time.time()

            return self.get_coordinates(check_age=False)

        except ValueError:
            pass

        return self.get_coordinates()


if __name__ == '__main__':
    print(    time.time())