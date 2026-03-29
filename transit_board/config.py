# ============================================================
# DISPLAY SETTINGS
# ============================================================

three_lines = True		# True: 3 lines per page, False: 2 lines per page
						#       (Each page is one cardinal direction)
color_by_line = False	# True: Line ID backgrounds shown in their brand colors:
						#       A train blue, D train purple, Rapid buses red, etc.
						# False: Line ID backgrounds colored by agency:
						#       Metro bus - orange, Metro rail - grey, LADOT - blue
color_arrivals = True	# True: arrival times color coded relative to walk time from home
						#		(stoplight style: red - will miss, yellow - leave now, green - good)
						# False: all arrival times shown in blue
						# 		(minutes_from_home still required; set to 0 to show all arrivals)
day_brightness = 100	# Brightness during the day (1-100)
night_brightness = 65	# Brightness at night (1-100)
						# Set both to the same value to disable auto-dimming


# ============================================================
# TRANSIT AGENCY DATA FOR YOUR STOPS
# ============================================================
# Enter data for one or more agency: L.A. Metro bus, L.A. Metro rail, and LADOT.
# Empty agency dicts will be skipped.
# L.A. Metro bus & rail require a Swiftly API key.

SWIFTLY_API_KEY = 'your_api_key'


# ============================================================
# LA METRO BUS
# Swiftly API endpoint: https://api.goswift.ly/real-time/lametro/gtfs-rt-trip-updates?format=json
#
# Recommended to populate this with the helper at:
# https://github.com/sleenhouts/LA-transit-board/blob/main/stop_helper.html
#
# For manual entry:
# Query: https://api.goswift.ly/info/lametro/routes?verbose=True
# Each route lists its directions (0 or 1) and the stops in each direction,
# with stop names and IDs. Match your station to a stop ID, note the
# direction ID (0 or 1), and assign a cardinal direction (for display) yourself.
# To get arrivals for both directions at one stop, include multiple entries as in the example.
# 
# direction: Cardinal direction the bus travels from this stop (N/S/E/W) for display
# minutes_from_home: Walking time from home to this stop
# ============================================================

my_stops_lametro = {
#	example:
#	'5137': [
#		{'route_id': '2', 'direction_id': '1', 'direction': 'W', 'minutes_from_home': 15},
#	],
#	'30000': [
#		{'route_id': '33', 'direction_id': '1', 'direction': 'W', 'minutes_from_home': 10},
#		{'route_id': '33', 'direction_id': '0', 'direction': 'W', 'minutes_from_home': 10},
#		{'route_id': '40', 'direction_id': '1', 'direction': 'S', 'minutes_from_home': 10},
#	],
}


# ============================================================
# LA METRO RAIL
# Swiftly API endpoint: https://api.goswift.ly/real-time/lametro-rail/gtfs-rt-trip-updates?format=json
#
# Recommended to populate this with the helper at:
# https://github.com/sleenhouts/LA-transit-board/blob/main/stop_helper.html
#
# For manual entry:
# Query: https://api.goswift.ly/info/lametro-rail/routes?verbose=True
# Each route lists its directions (0 or 1) and the stops in each direction,
# with stop names and IDs. Match your station to a stop ID, note the
# direction ID (0 or 1), and assign a cardinal direction (for display) yourself.
# To get arrivals for both directions at one stop, include multiple entries as in the example.
#
# direction: Cardinal direction the train travels from this stop (N/S/E/W) for display
# direction_id: The API's internal direction ID for this trip (0 or 1)
# minutes_from_home: Walking time from home to this station
# ============================================================

my_stops_lametrorail = {
#	example:
#	'80120': [
#		{'route_id': '801', 'direction_id': '0', 'direction': 'N', 'minutes_from_home': 3},
#		{'route_id': '801', 'direction_id': '1', 'direction': 'S', 'minutes_from_home': 3},
#	],
#	'80211': [
#		{'route_id': '805', 'direction_id': '1', 'direction': 'W', 'minutes_from_home': 20},
#	],
}

# ============================================================
# LADOT BUS
# stop IDs: The number after "/stops/" in your start_url (see below)
#
# direction: Cardinal direction the bus travels from this stop (N/S/E/W) for display
# minutes_from_home: Walking time from home to this stop
# route_id: The line abbreviation displayed — must be three characters or fewer for space
# start_url: The LADOT mobile arrivals URL for this stop and route.
#            Find it by navigating to your stop on ladotbus.com/m
# ============================================================

my_stops_ladot = {
#	example:
#	'305870': {
#		'direction': 'S',
#		'minutes_from_home': 10,
#		'route_id': 'MTD',
#		'start_url': 'https://www.ladotbus.com/m/regions/7/routes/576/direction/26733/stops/305870/pattern'
#	},
}
