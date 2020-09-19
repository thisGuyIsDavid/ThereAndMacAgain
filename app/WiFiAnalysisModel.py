from app.utils import haversine


class WiFiAnalysisModel:

	def __init__(self, **kwargs):
		self.name = kwargs.get('name')
		self.mac_address = kwargs.get('mac_address')

		self.vendor = kwargs.get('vendor')
		self.company_name = kwargs.get('company_name')

		self.is_node = kwargs.get('is_node')
		self.sighting_points = kwargs.get('sighting_points')

		self.connections = []
		self.set_sighting_connections()

	@staticmethod
	def set_from_sighting_data(sighting_data):
		return WiFiAnalysisModel(
			name=sighting_data.get('name'),
			mac_address=sighting_data.get('mac_address'),
			vendor=sighting_data.get('vendor'),
			company_name=sighting_data.get('company_name'),
			sighting_points=[
				{
					"lat_lng": [x.get('latitude'), x.get('longitude')],
					"date": x.get('date')
				} for x in sighting_data.get('sightings')]
		)

	def set_sighting_connections(self):
		for i, sighting in enumerate(self.sighting_points):
			# break on last sighting
			if i == len(self.sighting_points) - 1:
				break

			next_sighting = self.sighting_points[i + 1]
			distance = haversine(sighting.get('lat_lng')[1], sighting.get('lat_lng')[0], next_sighting.get('lat_lng')[1], next_sighting.get('lat_lng')[0])
			time_between = (next_sighting.get('date') - sighting.get('date')).total_seconds()

			self.connections.append(
				{
					"date_1": sighting.get('date'),
					"date_2": next_sighting.get('date'),
					"time_between": time_between,
					"lat_lng_1": sighting.get('lat_lng'),
					"lat_lng_2": next_sighting.get('lat_lng'),
					"distance": distance,
				}
			)

	def to_json(self):
		import datetime
		for sighting in self.sighting_points:
			sighting['date'] = sighting.get('date').isoformat() if type(sighting.get('date')) == datetime.datetime else sighting.get('date')

		for connection in self.connections:
			connection['date_1'] = connection.get('date_1').isoformat() if type(connection.get('date_1')) == datetime.datetime else connection.get('date_1')
			connection['date_2'] = connection.get('date_2').isoformat() if type(connection.get('date_2')) == datetime.datetime else connection.get('date_2')

		return {
			"mac_address": self.mac_address,
			"vendor": self.vendor,
			"company_name": self.company_name,
			"is_node": self.is_node,
			"sightings": self.sighting_points,
			"connections": self.connections
		}
