from app.LocalDatabaseService import LocalDatabaseService
from app.SQLiteProcessor import SQLiteProcessor
import datetime

class DataUploader:
    data_to_upload = []
    last_collection_date = None

    def set_data(self):
        results = SQLiteProcessor('/Users/davidhaverberg/PycharmProjects/ThereAndMacAgain/data.db').get_data()
        if results is None:
            return
        for result in results:
            result['when_recorded'] = datetime.datetime.strptime(result['when_recorded'][:-3], '%m/%d/%Y %H:%M:%S')
        self.data_to_upload = results

    def set_last_collection_date(self):
        result = LocalDatabaseService().get_row("""SELECT MAX(when_recorded) FROM mac_location_data LIMIT 1""")
        self.last_collection_date = result[0]

    def clean_data(self):
        if self.last_collection_date is None:
            return
        self.data_to_upload = [x for x in self.data_to_upload if x.get('when_recorded') > self.last_collection_date]
        self.data_to_upload = [x for x in self.data_to_upload if len(x.get('mac_address')) == 12]

    def insert_individuals(self):
        known_mac_addresses = [x[0] for x in LocalDatabaseService().get_all_rows("""SELECT DISTINCT id FROM mac_individuals""")]
        collected_mac_addresses = list(set([x.get('mac_address') for x in self.data_to_upload]))
        new_mac_addresses = [x for x in collected_mac_addresses if x not in known_mac_addresses]
        print("Found %s new mac addresses" % len(new_mac_addresses))
        LocalDatabaseService().insert_many(
            """
            INSERT IGNORE INTO mac_individuals (id) VALUES (%(id)s)
            """,
            [{'id': x} for x in new_mac_addresses]
        )

    def insert_collected_data(self):
        print('Inserting %s new records' % (len(self.data_to_upload)))
        LocalDatabaseService().insert_many(
            """
            INSERT IGNORE INTO mac_location_data (
                mac_address, latitude, longitude, when_recorded
            ) VALUES (
                %(mac_address)s, %(latitude)s, %(longitude)s, %(when_recorded)s
            )
            """, self.data_to_upload
        )

    def run(self):
        self.set_last_collection_date()
        self.set_data()
        self.clean_data()

        self.insert_individuals()
        self.insert_collected_data()


if __name__ == '__main__':
    DataUploader().run()
