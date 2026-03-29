# LA-transit-board

Shows Los Angeles public transit arrivals on an LED matrix. Can include arrival times from L.A. Metro and LADOT, optionally color-coded by how long it will take you to get to the stop from the board's location. Cycles through up to four pages for each of the cardinal directions, with two or three lines per page.

PICS TO COME

## Requires

* 64 x 32 RGB LED Matrix
* Raspberry Pi
* RGB Matrix Hat/Bonnet
* Power supply
* [hzeller/rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)
* Swiftly API key if you want L.A. Metro arrivals

Check out [Chuck Builds's LED Matrix Guide](https://www.chuck-builds.com/led-matrix/) for help with hardware assembly and setup.

If you use the compatible size matrix, Tom Hammond has a [3D-printable enclosure](https://www.thingiverse.com/thing:3779303) for it.

## Setup

After you have your hardware setup and rpi-rgb-led-matrix installed:

1. If you want L.A. Metro arrivals, request an API key from Swiftly at: [http://goswift.ly/realtime-api-key](http://goswift.ly/realtime-api-key)
2. Copy the entire transit_board directory to your Pi (including the fonts directory in it).
3. Copy [samplebase.py](https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/bindings/python/samples/samplebase.py) from the rpi-rgb-led-matrix python bindings samples folder to the transit_board directory.
4. Fill in your preferences in config.py - it's commented to explain the options.
5. For L.A. Metro arrivals, use the [stop helper](https://github.com/sleenhouts/LA-transit-board/blob/main/stop_helper.html) to create your stops list to paste into the config. 
6. `pip install` any missing dependencies - see the [requirements.txt](https://github.com/sleenhouts/LA-transit-board/blob/main/requirements.txt).
7. Run it! Run `sudo python3 board.py --led-rows=32 --led-cols=64` (+ any other rpi-rgb-led-matrix flags) to start. In your root cron jobs, `@reboot sleep 10 && until curl -s api.goswift.ly > /dev/null; do sleep 5; done; cd /home/pi/transit_board && python3 board.py --led-rows=32 --led-cols=64 > /home/pi/transit_board/error.txt 2>&1` will start the transit board when the matrix powers on and route errors to a log that's replaced on startup.
