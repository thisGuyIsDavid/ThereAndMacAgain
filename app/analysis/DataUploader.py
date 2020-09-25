from app.databases.LocalDatabaseService import LocalDatabaseService
from app.databases.SQLiteProcessor import SQLiteProcessor
import datetime


class DataUploader:
    data_to_upload = []
    last_collection_date = None

    def set_data(self):
        results = SQLiteProcessor('/Users/davidhaverberg/PycharmProjects/ThereAndMacAgain/tama.db').get_data()
        if results is None:
            return
        to_insert = []
        for result in results:
            try:
                result['when_recorded'] = datetime.datetime.strptime(result['when_recorded'][:-3], '%m/%d/%Y %H:%M:%S')
                to_insert.append(result)
            except ValueError:
                continue
        self.data_to_upload = to_insert

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

        to_insert = []
        for collected_mac_address in self.data_to_upload:
            if collected_mac_address.get('mac_address') in known_mac_addresses:
                continue
            if len(list(filter(lambda x: x.get('mac_address') == collected_mac_address.get('mac_address'), to_insert))) > 0:
                continue

            to_insert.append(collected_mac_address)

        print("Found %s new mac addresses" % len(to_insert))
        LocalDatabaseService().insert_many(
            """
            INSERT IGNORE INTO mac_individuals (id, name) VALUES (%(id)s, %(name)s)
            """,
            [{'id': x.get('mac_address'), 'name': x.get('name')} for x in to_insert]
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
