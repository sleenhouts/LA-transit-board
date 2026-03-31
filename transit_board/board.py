#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
from lametro import fetch_arrivals_swiftly, RAIL_ROUTES
from ladot import fetch_arrivals_ladot
from config import (three_lines, color_by_line, color_arrivals, day_brightness,
	night_brightness, SWIFTLY_API_KEY, my_stops_lametro, my_stops_lametrorail)
from astral import LocationInfo
from astral.sun import night
from backports.zoneinfo import ZoneInfo
from datetime import datetime
import time
import threading
import os

FONTS_DIR = os.path.join(os.path.dirname(__file__), 'fonts')


class BusBoard(SampleBase):
	def __init__(self, *args, **kwargs):
		super(BusBoard, self).__init__(*args, **kwargs)

	def run(self):
		canvas = self.matrix

		linefont = graphics.Font()
		arrivalsfont = graphics.Font()
		hmargin = 2

		if three_lines:
			linefont.LoadFont(os.path.join(FONTS_DIR, '5x8edit.bdf'))
			arrivalsfont.LoadFont(os.path.join(FONTS_DIR, '5x8edit.bdf'))
			linefixedcharwidth = 5
			arrivalsfixedcharwidth = 5
			vmargin = 3
		else:
			linefont.LoadFont(os.path.join(FONTS_DIR, '7x13B.bdf'))
			arrivalsfont.LoadFont(os.path.join(FONTS_DIR, '6x13edit.bdf'))
			linefixedcharwidth = 7
			arrivalsfixedcharwidth = 6
			vmargin = 2

		blue = graphics.Color(100,215,230)
		green = graphics.Color(51,255,51)
		yellow = graphics.Color(255,220,30)
		red = graphics.Color(235,19,27)
		black = graphics.Color(0,0,0)

		def backgroundcolor(lineid):
			agency = line_agency[lineid]
			if agency == 'ladot':
				return 'ladotblue'
			elif agency == 'lametro-rail':
				if color_by_line:
					return next(v['color'] for v in RAIL_ROUTES.values() if v['name'] == lineid[:-1])
				else:
					return 'railgrey'
			else:
				if color_by_line and lineid[:-1].isdigit() and 700 <= int(lineid[:-1]) <= 799:
					return 'busred'
				elif color_by_line and lineid[:-1] in ('910', '950'):
					return 'railgrey'
				else:
					return 'busorange'

		def drawLineIDBackground(text, backgroundcolor, textline): # not robust to font changes
			if three_lines:
				y_start = textline*vmargin+(textline-1)*linefont.height-2
				y_end = textline*(vmargin+linefont.height)-2
			else:
				y_start = textline*vmargin+(textline-1)*linefont.height+1
				y_end = textline*(vmargin+linefont.height)-1
			for y in range (y_start, y_end):
				for x in range (hmargin - 1, hmargin + len(text) * linefixedcharwidth):
					if backgroundcolor == 'busorange':
						canvas.SetPixel(x, y, 231, 80, 0) # Metro says (231,77,0), green bumped to read more orange
					elif backgroundcolor == 'busred':
						canvas.SetPixel(x, y, 175, 13, 50) # Metro claims (209, 18, 66), pulled less pink 
					elif backgroundcolor == 'ladotblue':
						canvas.SetPixel(x, y, 35, 70, 130) # logo picker is (25,55,105), but too dark
					elif backgroundcolor == 'railgrey':
						canvas.SetPixel(x, y, 128, 136, 141)
					elif isinstance(backgroundcolor, tuple):
						canvas.SetPixel(x, y, *backgroundcolor)

		# show only last red (missed by walk time) arrival
		def filterArrivals(values, lineid):
			last_red = None
			filtered = []
			for t in values:
				if t - line_minutes_from_home[lineid] < 1:
					last_red = t
				else:
					filtered.append(t)
			if last_red is not None:
				filtered.insert(0, last_red)
			return filtered

		# Convert lametro raw timestamps to minutes at display time; pass LADOT minutes through
		def resolveMinutes(values, lineid):
			if line_agency.get(lineid) in ('lametro', 'lametro-rail'):
				now = time.time()
				minutes = list({round((t - now) / 60) for t in values})
				return sorted(m for m in minutes if 0 < m < 60)
			return values

		if three_lines:
			num_arrivals = 3
		else:
			num_arrivals = 2

		def drawArrivalsByApproach(arrivaltext, lineid, textline):
			arrivals_list = arrivaltext.split(",")
			y = textline * arrivalsfont.height + (textline-1) * vmargin
			x = canvas.width - hmargin - len(arrivaltext) * arrivalsfixedcharwidth + 2

			for i, arrival in enumerate(arrivals_list):
				margin = int(arrival) - line_minutes_from_home[lineid]
				if color_arrivals:
					if margin < 1:
						color = red
					elif margin < 3:
						color = yellow
					elif margin < 8:
						color = green
					else:
						color = blue
				else:
					color = blue
				graphics.DrawText(canvas, arrivalsfont, x, y, color, arrival)
				x += len(arrival) * arrivalsfixedcharwidth
				if i < len(arrivals_list) - 1:
					graphics.DrawText(canvas, arrivalsfont, x, y, blue, ",")
					x += arrivalsfixedcharwidth

		# for nighttime dimming
		la = LocationInfo("Los Angeles", "USA", "America/Los_Angeles", 34.05, -118.25)
		la_tz = ZoneInfo("America/Los_Angeles")

		fetch_results = {'arrivals': {}, 'line_minutes_from_home': {}, 'line_agency': {}}
		fetch_lock = threading.Lock()

		def background_fetch():
			bus_arrivals, bus_minutes, bus_agency = fetch_arrivals_swiftly(
				my_stops_lametro,
				'https://api.goswift.ly/real-time/lametro/gtfs-rt-trip-updates?format=json',
				'lametro',
				SWIFTLY_API_KEY
			)
			rail_arrivals, rail_minutes, rail_agency = fetch_arrivals_swiftly(
				my_stops_lametrorail,
				'https://api.goswift.ly/real-time/lametro-rail/gtfs-rt-trip-updates?format=json',
				'lametro-rail',
				SWIFTLY_API_KEY
			)
			ladot_arrivals, ladot_minutes, ladot_agency = fetch_arrivals_ladot()
			bus_arrivals.update(rail_arrivals)
			bus_arrivals.update(ladot_arrivals)
			bus_minutes.update(rail_minutes)
			bus_minutes.update(ladot_minutes)
			bus_agency.update(rail_agency)
			bus_agency.update(ladot_agency)
			with fetch_lock:
				fetch_results['arrivals'] = bus_arrivals
				fetch_results['line_minutes_from_home'] = bus_minutes
				fetch_results['line_agency'] = bus_agency

		# kick off first fetch before loop starts
		fetch_thread = threading.Thread(target=background_fetch)
		fetch_thread.start()
		fetch_thread.join()  # wait for first fetch so board doesn't start with empty data

		# read initial data
		with fetch_lock:
			arrivals = dict(fetch_results['arrivals'])
			line_minutes_from_home = dict(fetch_results['line_minutes_from_home'])
			line_agency = dict(fetch_results['line_agency'])

		last_fetch_time = time.time()

		while True:
			# start next fetch in background immediately
			now = time.time()
			if now - last_fetch_time >= 10:
				fetch_thread = threading.Thread(target=background_fetch)
				fetch_thread.start()
				last_fetch_time = now

			# display more dimly at night
			n = night(la.observer, date=datetime.now(la_tz).date(), tzinfo=la_tz)
			if n[0] <= datetime.now(la_tz) <= n[1]:
				self.matrix.brightness = night_brightness
			else:
				self.matrix.brightness = day_brightness

			for directions in ["S","W","N","E"]:
				linecount=0
				text1R=''
				text1L=''
				text2R=''
				text2L=''
				text3R=''
				text3L=''
				for keys, values in sorted(arrivals.items()):
					if directions==keys[-1:] and linecount==0:
						text1L=keys
						text1R=','.join(str(t) for t in filterArrivals(resolveMinutes(values, keys), keys)[:num_arrivals])
						linecount=1
					elif directions==keys[-1:] and linecount==1:
						text2L=keys
						text2R=','.join(str(t) for t in filterArrivals(resolveMinutes(values, keys), keys)[:num_arrivals])
						linecount=2
					elif directions==keys[-1:] and linecount==2:
						text3L=keys
						text3R=','.join(str(t) for t in filterArrivals(resolveMinutes(values, keys), keys)[:num_arrivals])
						linecount=3

				if text1L != '':
					drawLineIDBackground(text1L,backgroundcolor(text1L),1)
					graphics.DrawText(canvas, linefont, hmargin, linefont.height, black, text1L)
					drawArrivalsByApproach(text1R,text1L,1)
					if text2R != '':
						drawLineIDBackground(text2L,backgroundcolor(text2L),2)
						graphics.DrawText(canvas, linefont, hmargin, 2 * linefont.height + vmargin, black, text2L)
						drawArrivalsByApproach(text2R,text2L,2)
					if text3R != '':
						drawLineIDBackground(text3L,backgroundcolor(text3L),3)
						graphics.DrawText(canvas, linefont, hmargin, 3 * linefont.height + 2 * vmargin, black, text3L)
						drawArrivalsByApproach(text3R,text3L,3)

					time.sleep(6) # show display for 6 seconds before next page
					canvas.Clear()
					time.sleep(0.8)

			# wait for fetch to finish if it hasn't already
			fetch_thread.join()

			# read new data for the next cycle
			with fetch_lock:
				arrivals = dict(fetch_results['arrivals'])
				line_minutes_from_home = dict(fetch_results['line_minutes_from_home'])
				line_agency = dict(fetch_results['line_agency'])

if __name__ == "__main__":
	bus_board = BusBoard()
	if (not bus_board.process()):
		bus_board.print_help()
