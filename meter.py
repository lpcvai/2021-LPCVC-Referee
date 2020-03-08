# THIS PROGRAM MUST BE RUN IN ADMIN MODE

from pyscreeze import ImageNotFoundException
from pyautogui import Point, click, moveTo, mouseDown, mouseUp, typewrite, locateOnScreen
from subprocess import Popen
import time
import os

MEASURE_MENU = Point(x=122, y=418)
REPORT_MENU = Point(x=117, y=538)
START_STOP = Point(x=433, y=262)
SAVE_CSV = Point(x=553, y=564)
SAVE_BTN = Point(x=1317, y=743)

BASE_COMMAND = 'cd ~/Documents/run_sub/ && python3 sub.py ~/Documents/test_data/video.MP4 ~/Documents/test_data/questions.txt'
FILENAME = "C:\\lpcvc\\pimetrics.csv"

def waitForImg(img, region, breakEarly=lambda:False):
	"""
	Loop until a certain image appears on the screen in the region.

	Parameters:
	  img: filename or path of the image
	  region: 4 entry tuple consisting of the (leftBound, topBound, width, height)
	  breakEarly (optional): condition to see if the loop should terminate early

 	Return: was breakEarly() true
	"""
	while not breakEarly():
		try:
			if (locateOnScreen(img, region=region) is not None):
				return False
		except ImageNotFoundException:
			time.sleep(.01)
	return True

def startMeter():
	"""
	Use hotkeys to start the power meter.
	"""
	click(MEASURE_MENU)
	click(START_STOP)
	waitForImg("stop.png", region=(326, 234, 216, 59))
	#startUserCode()
	#waitForImg("start.png", region=(651, 772, 909-651, 806-772))

def stopMeter(filename=FILENAME):
	"""
	Use hotkeys to save the power meter data to a file.
	"""
	time.sleep(1.5)
	click(REPORT_MENU)
	click(SAVE_CSV)
	time.sleep(1.5)
	typewrite(filename)
	click(SAVE_BTN)
	time.sleep(1.5)

def cycle(command=BASE_COMMAND):
	"""
	Start the command specified and wait until the meter times out or the process terminates early.
	"""
	proc = Popen(['C:\\Windows\\System32\\bash.exe', '-c', 'ssh -t pi@referee.local "' + command + '"'])

	def breakEarly():
		return proc.poll() is not None

	startMeter()
	#waitForImg("7s.png", region=(1117, 643, 1208-1117, 694-643))
	waitForImg("start.png", region=(326, 234, 216, 59), breakEarly=breakEarly)

	# Click the stop button if needed
	if breakEarly():
		click(START_STOP)
	else:
		proc.terminate()
	#time.sleep(10)
	#proc.kill()
	stopMeter()

#def stopPi():
	#cmdText = ' '.join(['ssh', '-t', 'pi@referee.local', f'{BASE_COMMAND}"'])
	#cmd('pkill', '-f', f"'{cmdText}'")

startCycle = True

from flask import Flask, send_file

app = Flask(__name__)

@app.route("/")
def haobo():
	global startCycle
	try:
		os.remove(FILENAME)
	except:
		pass
	if startCycle:
		startCycle = False
		cycle()
		startCycle = True
		try:
			return send_file(FILENAME)
		except:
			return ""
	return "Task Already Running"
