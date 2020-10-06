from app.databases.LocalDatabaseService import LocalDatabaseService
from app.utils import haversine


class ClusterSetter:
	known_cluster_points = []
	unknown_cluster_points = []
	locations_to_cluster = []
	locations_to_update = []

	def clear_location_ids(self):
		LocalDatabaseService().update(
			"""
			UPDATE mac_location_data SET location_id = NULL
            """, {}
		)

	def delete_unknown_locations(self):
		LocalDatabaseService().update(
			"""
			DELETE FROM mac_locations 
			WHERE id NOT IN (
				SELECT DISTINCT location_id 
				FROM mac_location_data 
				WHERE location_id is not NULL 
				ORDER BY location_id ASC
			) AND name = 'UNKNOWN LOCATION'
			""", {}
		)

	def set_known_cluster_points(self):
		results = LocalDatabaseService().get_all_rows(
			"""
			SELECT id, latitude, longitude, location_radius 
			FROM mac_locations 
			WHERE type IS NOT NULL
			"""
		)
		self.known_cluster_points = [
			{
				"id": result[0],
				"latitude": result[1],
				"longitude": result[2],
				"radius": result[3]
			} for result in results
		]

	def set_locations_to_cluster(self):
		results = LocalDatabaseService().get_all_rows(
			"""
			SELECT latitude, longitude, count(*) 
			FROM mac_location_data 
			GROUP BY latitude, longitude 
			ORDER BY count(*) DESC
			"""
		)
		self.locations_to_cluster = [
			{
				"latitude": result[0],
				"longitude": result[1],
				"count": result[2]
			} for result in results
		]

	def run_cluster_process(self):
		for location_to_cluster in self.locations_to_cluster:
			for known_cluster_point in self.known_cluster_points:
				distance_between_location_and_cluster = haversine(
					location_to_cluster.get('longitude'),
					location_to_cluster.get('latitude'),
					known_cluster_point.get('longitude'),
					known_cluster_point.get('latitude')
				)

				if distance_between_location_and_cluster <= known_cluster_point.get('radius'):
					self.locations_to_update.append({
						"location_id": known_cluster_point.get('id'),
						"latitude": location_to_cluster.get('latitude'),
						"longitude": location_to_cluster.get('longitude')
					})
					break
		self.update_locations()

	def update_locations(self):
		LocalDatabaseService().update_many(
			"""
			UPDATE mac_location_data SET location_id=%(location_id)s WHERE latitude=%(latitude)s AND longitude=%(longitude)s
			""", self.locations_to_update
		)

	def set_unknown_cluster_points(self):
		results = LocalDatabaseService().get_all_rows(
			"""
			SELECT latitude, longitude, count(*) FROM (
				SELECT mac_address, ROUND(latitude, 3) AS latitude,  ROUND(longitude, 3) AS longitude
				FROM mac_location_data 
				WHERE location_id IS NULL
				GROUP BY  ROUND(latitude, 3), ROUND(longitude, 3), mac_address
			) AS seen_macs
			GROUP BY latitude, longitude
			ORDER BY count(*) DESC
			"""
		)
		self.unknown_cluster_points = [
			{
				"name": "UNKNOWN LOCATION",
				"latitude": result[0],
				"longitude": result[1]
			} for result in results if result[2] >= 100
		]

	def insert_unknown_cluster_points(self):
		LocalDatabaseService().insert_many(
			"""
			INSERT INTO mac_locations (name, latitude, longitude) 
			VALUES (%(name)s, %(latitude)s, %(longitude)s)
			""", self.unknown_cluster_points
		)
		print('Added %s new clusters' % len(self.unknown_cluster_points))

	def process(self):
		self.clear_location_ids()

		# process known cluster points
		self.set_known_cluster_points()
		self.set_locations_to_cluster()
		self.run_cluster_process()

		return
		# process unknown_cluster points
		self.set_unknown_cluster_points()
		self.insert_unknown_cluster_points()
		self.run_cluster_process()

		self.delete_unknown_locations()


if __name__ == '__main__':
	ClusterSetter().process()


