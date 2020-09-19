# !/usr/bin/env python
from app.collector.SerialCollector import SerialCollector


class GPSCollector(SerialCollector):

    def process_line(self, line):
        # check gps connection
        if '*' in line:
            return

        gps_array = [x for x in line.strip().split('|') if x != '']

        try:
            latitude = round(float(gps_array[0]), 4)
            longitude = round(float(gps_array[1]), 4)
        except ValueError:
            return

        return {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "timestamp": gps_array[2]
        }