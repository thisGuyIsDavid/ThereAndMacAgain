import json
import datetime
from app.databases.LocalDatabaseService import LocalDatabaseService

to_insert = []
to_update = []
to_replace = []

rows = [{'id': x[0],'vendor': x[1]} for x in LocalDatabaseService().get_all_rows("SELECT id, vendor FROM mac_vendors")]


with open('/Users/davidhaverberg/Downloads/macaddress.io-db.json', encoding='utf-8') as json_lines:
    for line in json_lines:
        json_line = json.loads(line.strip())
        if len(json_line.get('oui')) > 8:
            continue
        insert_map = {
            'id': json_line.get('oui').replace(":", "").upper(),
            'vendor': json_line.get('companyName'),
            'date_updated': datetime.datetime.strptime(json_line.get('dateUpdated'), '%Y-%m-%d'),
            'country_code': json_line.get('countryCode')
        }
        if insert_map.get('date_updated') < datetime.datetime(2019, 9, 1):
            continue

        matches_mac = list(filter(lambda x: insert_map.get('id') == x.get('id'), rows))
        if matches_mac == 0:
            to_insert.append(matches_mac)
            continue

        matches_mac_and_name = list(filter(lambda x: insert_map.get('vendor') == x.get('vendor'), matches_mac))

        if len(matches_mac) == 1 and len(matches_mac_and_name) == 0:
            to_replace.append(insert_map)
            continue

        if len(matches_mac) == 1 and len(matches_mac_and_name) == 1:
            to_update.append(insert_map)

LocalDatabaseService().insert_many(
    """
    REPLACE INTO mac_vendors (
        id, vendor, country_code, date_updated
    ) VALUES (
        %(id)s, %(vendor)s, %(country_code)s, %(date_updated)s
    )
    """, to_replace
)

LocalDatabaseService().insert_many(
    """
    INSERT INTO mac_vendors (
        id, vendor, country_code, date_updated
    ) VALUES (
        %(id)s, %(vendor)s, %(country_code)s, %(date_updated)s
    )
    """, to_insert
)

LocalDatabaseService().update_many(
    """
    UPDATE mac_vendors SET country_code = %(country_code)s, date_updated=%(date_updated)s WHERE id=%(id)s
    """, to_update
)


print(len(to_insert), len(to_replace), len(to_update))