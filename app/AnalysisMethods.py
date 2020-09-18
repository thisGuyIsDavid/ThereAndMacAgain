from app.LocalDatabaseService import LocalDatabaseService
import datetime
from app.utils import haversine

class DateAnalysis:

    def __init__(self, date_to_check=datetime.date.today()):
        self.date_to_check = date_to_check
        self.mac_data = self.get_data()

    def get_data(self):
        results = LocalDatabaseService().get_all_rows_with_values(
            """
            SELECT 
                encountered_macs.mac_address, encountered_macs.first_seen, encountered_macs.last_seen, 
                vendor, mac_vendor_companies.name, mac_vendor_companies.type,
	            first_seen_location.name, first_seen_location.type, first_seen.latitude, first_seen.longitude, 
	            last_seen_location.name, last_seen_location.type,last_seen.latitude, last_seen.longitude
            FROM 
            (	
                SELECT mac_address, MIN(when_recorded) AS first_seen, MAX(when_recorded) AS last_seen, 
                TIMESTAMPDIFF(HOUR, MIN(when_recorded), MAX(when_recorded)) AS time_diff
                FROM mac_location_data 
                GROUP BY mac_address
            ) AS encountered_macs
            
            JOIN mac_location_data AS first_seen
                ON first_seen.mac_address = encountered_macs.mac_address AND first_seen.when_recorded = encountered_macs.first_seen
            LEFT JOIN mac_locations AS first_seen_location
                ON first_seen_location.id = first_seen.location_id
            
            JOIN mac_location_data AS last_seen
                ON last_seen.mac_address = encountered_macs.mac_address AND last_seen.when_recorded = encountered_macs.last_seen
            LEFT JOIN mac_locations AS last_seen_location
                ON last_seen_location.id = last_seen.location_id
            
            JOIN mac_individuals
                ON mac_individuals.id = encountered_macs.mac_address
            JOIN mac_vendors
                ON mac_vendors.id = LEFT(encountered_macs.mac_address, 6)
            LEFT JOIN mac_vendor_companies
                ON mac_vendor_companies.id = mac_vendors.company_id
            WHERE time_diff > 12
            AND encountered_macs.mac_address IN (
                SELECT DISTINCT mac_address 
                FROM mac_location_data 
                WHERE DATE(when_recorded) = %(date_to_check)s
            )
            ORDER BY first_seen
            """,
            {
                'date_to_check': self.date_to_check
            }
        )
        return [
            {
                'mac_address': result[0],
                'first_seen': result[1],
                'last_seen': result[2],
                'vendor': result[3],
                'company_name': result[4],
                'company_type': result[5],

                'first_location_name': result[6],
                'first_location_type': result[7],
                'first_latitude': result[8],
                'first_longitude': result[9],

                'last_location_name': result[10],
                'last_location_type': result[11],

                'last_latitude': result[12],
                'last_longitude': result[13],
            }
            for result in results
        ]

    def analyze(self):
        for mac in self.mac_data:
            print(mac.get('mac_address'))
            print('First Sighting: ')
            print(mac.get('first_latitude'), mac.get('first_longitude'), mac.get('last_latitude'), mac.get('last_longitude'))
            distance = haversine(mac.get('first_latitude'), mac.get('first_longitude'), mac.get('last_latitude'), mac.get('last_longitude'))
            print(round(distance, 2))


DateAnalysis().analyze()