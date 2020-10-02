from app.collector.MainCollector import MainCollector

if __name__ == '__main__':
    MainCollector(wifi_port='/dev/ttyUSB1', gps_port='/dev/ttyUSB0').run()