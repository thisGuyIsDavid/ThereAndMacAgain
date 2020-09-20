import json
from itertools import combinations
from app.analysis.WiFiAnalysisModel import WiFiAnalysisModel
from app.databases.LocalDatabaseService import LocalDatabaseService
from app.utils import haversine


class BuildSightingData:
	def __init__(self):
		self.sighting_data = []
		self.sighting_models = []
		self.links = []
		self.nodes = []

	def set_sighting_data(self):
		result_map = {}
		results = LocalDatabaseService().get_all_rows(
			"""
			SELECT encountered_macs.mac_address, latitude, longitude, when_recorded, mac_vendors.vendor, mac_individuals.name, mac_vendor_companies.name, is_node, mac_data.name
			FROM (
				SELECT mac_address FROM 
					#	mac addresses that have been seen at least one hour apart.
					(	
						SELECT mac_address, TIMESTAMPDIFF(HOUR, MIN(when_recorded), MAX(when_recorded)) AS time_diff
						FROM mac_location_data 
						GROUP BY mac_address
					) AS acceptable_macs
    			WHERE time_diff > 12
    		) AS encountered_macs
			JOIN
				(
					SELECT mac_address, 
						IF(mac_locations.id IS NULL, ROUND(mac_location_data.latitude, 4), ROUND(mac_locations.latitude, 4)) AS latitude, 
						IF(mac_locations.id IS NULL, ROUND(mac_location_data.longitude, 4), ROUND(mac_locations.longitude, 4)) AS longitude, 
						when_recorded, mac_locations.id IS NULL AS is_node, mac_locations.name
					FROM mac_location_data
					LEFT JOIN mac_locations
						ON mac_locations.id = mac_location_data.location_id	
				) AS mac_data
				ON mac_data.mac_address = encountered_macs.mac_address
			JOIN mac_individuals
				ON mac_individuals.id = encountered_macs.mac_address
			JOIN mac_vendors
				ON mac_vendors.id = LEFT(encountered_macs.mac_address, 6)
			JOIN mac_vendor_companies
				ON mac_vendor_companies.id = mac_vendors.company_id
			WHERE mac_individuals.ignore = 0
			AND mac_vendor_companies.ignore = 0
						AND YEAR(when_recorded) = 2020

			ORDER BY mac_individuals.id, when_recorded
			
			"""
		)
		for mac_address in set([result[0] for result in results]):
			specific_records = list(filter(lambda x: x[0] == mac_address, results))
			mac_address_record = {
				"mac_address": specific_records[0][0],
				"vendor": specific_records[0][4],
				"company_type": specific_records[0][5],
				"company_name": specific_records[0][6],
				"is_node": specific_records[0][7],
				"sightings": [
					{
						"latitude": result[1],
						"longitude": result[2],
						"date": result[3],
						"location_type": result[8],
					} for result in specific_records
				]
			}
			self.sighting_data.append(mac_address_record)

	def clean_sighting_data(self):
		cleaned_data = []
		for seen_mac_address in self.sighting_data:

			#	clean sightings if they're clumped too closely in time.
			cleaned_sightings = self.clean_by_time(seen_mac_address.get('sightings'))

			#	clean sightings if they're clumpled too closely in location.
			distance = [haversine(x.get('longitude'), x.get('longitude'),y.get('longitude'), y.get('longitude')) for x, y in combinations(cleaned_sightings, 2)]

			if sum(distance) == 0:
				continue

			# along with mobile devices, Google makes WiFi routers. Clean those.
			if seen_mac_address.get('company_name') == "Google" and (sum(distance) / len(distance)) < 3:
				continue

			if len(cleaned_sightings) == 1:
				continue

			seen_mac_address['sightings'] = cleaned_sightings
			cleaned_data.append(seen_mac_address)
		self.sighting_data = cleaned_data

	@staticmethod
	def clean_by_time(data_points):
		array_to_return = []
		for i, data_point in enumerate(data_points):
			# no matter what, include the first data point
			if i == 0:
				array_to_return.append(data_point)
				continue
			# get the last data point added. Array will never be empty at this point.
			most_recently_added_data_point = array_to_return[len(array_to_return) - 1]
			time_between = (data_point.get('date') - most_recently_added_data_point.get('date')).seconds
			if time_between < 7200:
				continue
			array_to_return.append(data_point)
		return array_to_return

	def set_location_nodes(self):
		node_dictionary = {}

		for sighting_data_point in self.sighting_data:
			for sighting in sighting_data_point.get('sightings'):
				key = "%s_%s" % (sighting.get('latitude'), sighting.get('longitude'))

				if key in node_dictionary:
					node_dictionary[key]['count'] += 1
				else:
					node_dictionary[key] = {
						"lat_lng": [sighting.get('latitude'), sighting.get('longitude')],
						"name": sighting.get('location_type'),
						"count": 1
					}

		self.nodes = [value for key, value in node_dictionary.items()]

	def create_json(self):
		with open('/Users/davidhaverberg/PhpstormProjects/thisguyisdavidvue/src/assets/data/dataset.json', 'w') as dataset:
			dataset.write(
				json.dumps({
					"nodes": self.nodes,
					"connections": [model.to_json() for model in self.sighting_models]
				})
			)

	def process(self):
		self.set_sighting_data()
		self.clean_sighting_data()

		self.sighting_models = [WiFiAnalysisModel.set_from_sighting_data(sighting_data_point) for sighting_data_point in self.sighting_data]
		self.set_location_nodes()
		self.create_json()
		return [model.to_json() for model in self.sighting_models]


if __name__ == '__main__':
	BuildSightingData().process()
