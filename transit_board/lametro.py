import requests
import orjson
import time

# Colors adjusted to read more correct or distinct. Original values commented.
RAIL_ROUTES = {
	'801': {'name': 'A', 'color': (0, 114, 188)},
	'802': {'name': 'B', 'color': (235, 19, 27)},
	'803': {'name': 'C', 'color': (56, 167, 90)}, #(88, 167, 56)
	'804': {'name': 'E', 'color': (253, 185, 19)},
	'805': {'name': 'D', 'color': (130, 70, 210)}, #(160, 93, 165)
	'807': {'name': 'K', 'color': (228, 96, 160)}, #(229, 109, 177)
}

def fetch_arrivals_swiftly(stops, url, agency, api_key):
	arrivals = {}
	line_minutes_from_home = {}
	line_agency = {}

	if not stops:
		return arrivals, line_minutes_from_home, line_agency

	try:
		r = requests.get(url, headers={'Authorization': api_key}, timeout=10)
		r.raise_for_status()
		data = orjson.loads(r.content)
	except Exception as e:
		print("Swiftly API error:", e)
		return arrivals, line_minutes_from_home, line_agency

	now = time.time()

	for entity in data.get('entity', []):
		tu = entity.get('tripUpdate', {})
		feed_route_id = tu.get('trip', {}).get('routeId', '').split('-')[0]  # "-13196" suffixes stripped
		feed_direction_id = str(tu.get('trip', {}).get('directionId', ''))

		for stu in tu.get('stopTimeUpdate', []):
			stop_id = stu.get('stopId', '')

			if stop_id not in stops:
				continue
			if stu.get('scheduleRelationship') not in ('SCHEDULED', 'ADDED', 'UNSCHEDULED'):
				continue

			arrival_info = stu.get('arrival') or stu.get('departure', {})
			arrival_timestamp = arrival_info.get('time')
			if not arrival_timestamp:
				continue

			minutes_away = round((int(arrival_timestamp) - now) / 60)
			if not (0 < minutes_away < 60):
				continue

			matched = [e for e in stops[stop_id]
				if e['route_id'] == feed_route_id
				and e['direction_id'] == feed_direction_id]
			if not matched:
				continue

			stop_info = matched[0]

			if agency == 'lametro-rail':
				display_route_id = RAIL_ROUTES[feed_route_id]['name']
			else:
				display_route_id = feed_route_id

			line = display_route_id + stop_info['direction']

			if line not in arrivals:
				arrivals[line] = []
				line_minutes_from_home[line] = stop_info['minutes_from_home']
				line_agency[line] = agency

			if minutes_away not in arrivals[line]:
				arrivals[line].append(minutes_away)

	for line in arrivals:
		arrivals[line].sort()

	return arrivals, line_minutes_from_home, line_agency


# if __name__ == "__main__":	# to test module in CLI - remove rail/-rail 4 lines for bus
# 	from config import SWIFTLY_API_KEY, my_stops_lametrorail
# 	arrivals, line_minutes_from_home, line_agency = fetch_arrivals_swiftly(
# 		my_stops_lametrorail,
# 		'https://api.goswift.ly/real-time/lametro-rail/gtfs-rt-trip-updates?format=json',
# 		'lametro-rail',
# 		SWIFTLY_API_KEY
# 	)
# 	print("Arrivals:", arrivals)
# 	print("Walk times:", line_minutes_from_home)
# 	print("Agencies:", line_agency)