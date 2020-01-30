# THIS PROGRAM MUST BE RUN IN ADMIN MODE

from pyscreeze import ImageNotFoundException
from pyautogui import Point, click, moveTo, mouseDown, mouseUp, typewrite, locateOnScreen
from subprocess import run as cmd
import time

MEASURE_MENU = Point(x=122, y=418)
REPORT_MENU = Point(x=117, y=538)
START_STOP = Point(x=433, y=262)
SAVE_CSV = Point(x=553, y=564)
SAVE_BTN = Point(x=1317, y=743)

def waitForImg(img, region):
	while True:
		try:
			if (locateOnScreen(img, region=region) is not None):
				break
		except ImageNotFoundException:
			time.sleep(.01)

def startMeter():
	click(MEASURE_MENU)
	click(START_STOP)
	waitForImg("stop.png", region=(326, 234, 216, 59))
	#startPi()
	#waitForImg("start.png", region=(651, 772, 909-651, 806-772))

def stopMeter():
	time.sleep(1.5)
	click(REPORT_MENU)
	click(SAVE_CSV)
	time.sleep(1.5)
	typewrite("pimetrics.csv")
	click(SAVE_BTN)
	time.sleep(1.5)

def cycle():
	startMeter()
	#waitForImg("7s.png", region=(1117, 643, 1208-1117, 694-643))
	waitForImg("start.png", region=(326, 234, 216, 59))
	#stopPi()
	stopMeter()


# PI
def startPi():
	cmd('start', 'ssh', 'pi@referee.local', '"python3 ./code.py"')

def stopPi():
	cmd('ssh', 'pi@referee.local', '"ps ax | grep code.py | killall -9"')

def main():
	#while True:
	#	if (input("Start? [y] ") != 'y'):
	#		break
	cycle()

if __name__ == "__main__":
	main()

