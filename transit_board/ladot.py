import requests
import re
from config import my_stops_ladot

API_BASE_URL = 'https://www.ladotbus.com/api/rtpi'
STOP_URL_PATTERN = re.compile(r'/route/(\d+)/direction/([^/]+)/stop/(\d+)')

# route_id -> {direction_slug: direction_id}, resolved once per process run
_direction_id_cache = {}


def _slugify(direction_text):
	return direction_text.lower().replace(' ', '-')


def _get_direction_id(route_id, direction_slug):
	if route_id not in _direction_id_cache:
		try:
			r = requests.get(API_BASE_URL, params={'path': f'routes/{route_id}/patterns'}, timeout=10)
			r.raise_for_status()
			patterns = r.json()
			_direction_id_cache[route_id] = {_slugify(p['direction']): p['id'] for p in patterns}
		except Exception as e:
			print("LADOT error fetching directions for route", route_id, ":", e)
			_direction_id_cache[route_id] = {}

	return _direction_id_cache[route_id].get(direction_slug)


def fetch_arrivals_ladot():
	arrivals = {}
	line_minutes_from_home = {}
	line_agency = {}

	for stop_id, info in my_stops_ladot.items():
		match = STOP_URL_PATTERN.search(info['start_url'])
		if not match:
			print("LADOT: could not parse route/direction/stop from start_url for stop", stop_id)
			continue
		route_id, direction_slug, api_stop_id = match.groups()

		direction_id = _get_direction_id(route_id, direction_slug)
		if direction_id is None:
			print("LADOT: could not resolve direction '" + direction_slug + "' for route", route_id, "(stop", stop_id, ")")
			continue

		try:
			path = f'stops/{api_stop_id}/arrivals?routeId={route_id}'
			r = requests.get(API_BASE_URL, params={'path': path}, timeout=10)
			r.raise_for_status()
			data = r.json()
		except Exception as e:
			print("LADOT request error for stop", stop_id, ":", e)
			continue

		try:
			line = info['route_id'] + info['direction']
			line_minutes_from_home[line] = info['minutes_from_home']
			line_agency[line] = 'ladot'

			for item in data:
				pattern = item.get('pattern') or {}
				if pattern.get('id') != direction_id:
					continue
				seconds_to_arrival = item.get('secondsToArrival')
				if seconds_to_arrival is None:
					continue
				minutes_away = round(seconds_to_arrival / 60)
				if 0 < minutes_away < 60:
					if line not in arrivals:
						arrivals[line] = []
					if minutes_away not in arrivals[line]:
						arrivals[line].append(minutes_away)

		except Exception as e:
			print("LADOT parsing error for stop", stop_id, ":", e)
			continue

	for line in arrivals:
		arrivals[line].sort()

	return arrivals, line_minutes_from_home, line_agency


# if __name__ == "__main__": # for CLI test module
# 	arrivals, line_minutes_from_home, line_agency = fetch_arrivals_ladot()
# 	print("Arrivals:", arrivals)
# 	print("Walk times:", line_minutes_from_home)
# 	print("Agencies:", line_agency)
