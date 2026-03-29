import requests
import re
from bs4 import BeautifulSoup
from config import my_stops_ladot


def fetch_arrivals_ladot():
    arrivals = {}
    line_minutes_from_home = {}
    line_agency = {}

    for stop_id, info in my_stops_ladot.items():
        try:
            r = requests.get(info['start_url'], timeout=10)
            r.raise_for_status()
        except Exception as e:
            print("LADOT request error for stop", stop_id, ":", e)
            continue

        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            arrivals_list = soup.find('ul', class_='arrivals')
            if not arrivals_list:
                print("LADOT: no arrivals list found for stop", stop_id)
                continue

            line = info['route_id'] + info['direction']
            line_minutes_from_home[line] = info['minutes_from_home']
            line_agency[line] = 'ladot'

            for li in arrivals_list.find_all('li'):
                strong = li.find('strong')
                if strong:
                    match = re.search(r'in (\d+) min', strong.text)
                    if match:
                        minutes_away = int(match.group(1))
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
#     arrivals, line_minutes_from_home, line_agency = fetch_arrivals_ladot()
#     print("Arrivals:", arrivals)
#     print("Walk times:", line_minutes_from_home)
#     print("Agencies:", line_agency)