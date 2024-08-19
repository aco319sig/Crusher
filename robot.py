from gpiozero import Button, Motor, PWMLED
from time import sleep
import drivers, socket, sys
from time import time as ti

class Robot:
	"""Creates Robot Class

	Expected Values:

	crush_motor = Motor(forward=23, backward=24)
	crush_limit = Button(17)
	retract_limit = Button(25)
	lid_safety = Button(4)
	start_button = Button(16)
	e_stop = Button(12)
	disp_sda = 2
	disp_scl = 3
	"""

	def __init__(self, crush_pin=23, retract_pin=24, crush_limit=17, retract_limit=25, start_pin=16, e_stop_pin=12, lid_pin=4, led_pin=26):
		super(Robot, self).__init__()
		self.motor = Motor(crush_pin, retract_pin)
		self.c_limit = Button(crush_limit)
		self.r_limit = Button(retract_limit)
		self.start_button = Button(start_pin)
		self.estop_button = Button(e_stop_pin)
		self.lid_safe = Button(lid_pin)
		self.led = PWMLED(pin=led_pin, initial_value=0)
		self.lcd = drivers.Lcd()
		self.all_stop = False

	def fade_led(self, state, fade_delay=2, background=True):
		if state == 1:
			self.led.blink(on_time=0, off_time=0, fade_in_time=fade_delay, fade_out_time=0, n=1, background=background)
			self.led.on()
		elif state == 0:
			self.led.blink(on_time=0, off_time=0, fade_in_time=0, fade_out_time=fade_delay, n=1, background=background)
			self.led.off()

	def disp_text(self, l1='skip', l2='skip', j2='l', j1='l', cl=True, bkon=True):
		if cl:
			self.lcd.lcd_clear()
		if bkon:
			self.lcd.lcd_backlight(1)
		else:
			self.lcd.lcd_backlight(0)
		if not l1 == 'skip':
			l1 = str(l1)
			if len(l1) < 16:
				if j1 == 'r':
					l1 = l1.rjust(16)
				elif j1 == 'c':
					l1 = l1.center(16)
				else:
					l1 = l1.ljust(16)
			self.lcd.lcd_display_string(l1, 1)
		if not l2 == 'skip':
			l2 = str(l2)
			if len(l2) < 16:
				if j2 == 'r':
					l2 = l2.rjust(16)
				elif j2 == 'c':
					l2 = l2.center(16)
				else:
					l2 = l2.ljust(16)
			self.lcd.lcd_display_string(l2, 2)

	def get_ip(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.settimeout(0)
		try:
			# doesn't even have to be reachable
			self.s.connect(('10.254.254.254', 1))
			IP = self.s.getsockname()[0]
		except Exception:
			IP = '127.0.0.1'
		finally:
			self.s.close()
		return IP

	def crush_motor_test(self):
		if not self.c_limit.is_pressed:
			self.motor.forward()
			sleep(2)
			self.motor.stop()
			return True
		else:
			print("Crush arm is already at full extension!")
			return False

	def retract_motor_test(self):
		if not self.r_limit.is_pressed:
			self.motor.backward()
			self.r_limit.wait_for_press()
			self.motor.stop()
			return True
		else:
			print("Crush arm is already at home!")
			return False

	def home(self, n=28):
		delay = ti() + n
		if not self.r_limit.is_pressed:
			self.disp_text('Homing crusher', j1='c')
			self.motor.backward()
			while not self.r_limit.is_pressed:
				if ti() > delay:
					self.motor.stop()
					self.disp_text('Home took', 'too long!', j1='c', j2='c')
					sleep(3)
					self.disp_text('Check for Jam', 'or Brkn switch!')
					return False
				else:
					sleep(0.2)
			self.motor.stop()
			self.disp_text(cl=False, l2='Ready!')
			sleep(0.5)
			return True
		else:
			self.disp_text(cl=False, l2='Ready!')
			return True

	def lid_check(self, n=10):
		delay = ti() + n
		if not self.lid_safe.is_pressed:
			self.disp_text('Close Lid!!')
			self.fade_led(state=1, fade_delay=2, background=True)
			while not self.lid_safe.is_pressed:
				sleep(0.25)
				if ti() > delay:
					self.disp_text(cl=False, l2='Timeout = 10 sec')
					return False
			self.disp_text(cl=False, l2='Lid is closed')
			self.fade_led(state=0, fade_delay=2, background=False)
			sleep(0.5)
			return True
		else:
			return True

	def _crush(self):
		if self.lid_check(10):
			if not self.c_limit.is_pressed:
				delay = ti() + 30
				self.disp_text('Crushing...')
				self.fade_led(state=1, fade_delay=1, background=False)
				self.motor.forward()
				while not self.c_limit.is_pressed:
					if ti() > delay:
						self.motor.stop()
						self.disp_text('Crush took', 'too long!')
						sleep(3)
						self.disp_text('Check for Jam!', j1='c')
						return False
					else:
						sleep(0.2)
				self.motor.stop()
				self.disp_text(cl=False, l2='...Done!', j2='r')
				sleep(0.5)
				if self.home():
					self.disp_text('Press Start', 'to begin...', j1='c', j2='c')
					self.fade_led(state=0, fade_delay=2, background=False)
					return True
			else:
				self.disp_text('Crusher not set')
				sleep(0.5)
				if self.home():
					self.disp_text('Press Start', 'Again!', j1='c', j2='c')
					self.fade_led(state=0, fade_delay=2, background=False)
				else:
					self.disp_text('Check for Jam!')
					sleep(1)
					return False
		else:
			self.disp_text('Lid Must Be', 'Closed To Run')
			return False

	def reset_pi(self):
		self.disp_text('RESETTING...')
		sys.exit()

	def e_stop(self):
		delay = ti() + 3
		timeout = True
		self.all_stop = True
		self.motor.stop()
		self.disp_text('Emergency Stop', 'Pressed')
		while timeout:
			if ti() > delay:
				timeout = False
			else:
				self.lcd.lcd_backlight(0)
				sleep(0.2)
				self.lcd.lcd_backlight(1)
				sleep(0.2)
		sleep(3)
		self.disp_text('Power Cycle', 'to Restart', j1='c', j2='c')
		print("Emergency Stop Pressed!")
		self.fade_led(state=0, fade_delay=4, background=False)
		sys.exit()

	def cycle(self):
		if not self.r_limit.is_pressed:
			self.home()
			sleep(1)
			self.disp_text('Press Start', 'to begin...', j1='c', j2='c')

		try:
			while True:
				first = self.start_button.value
				sleep(0.05)
				second = self.start_button.value
				if first and not second:
					self.disp_text('Start Pressed')
				elif not first and second:
					self.disp_text(l2='Start released!', cl=False)
					self._crush()
				elif not self.lid_safe.value:
					self.disp_text('Lid Open!')
					while not self.lid_safe.is_pressed:
						if not self.led.is_active:
							self.fade_led(state=1, fade_delay=2, background=False)
					self.disp_text('Press Start', 'to begin...', j1='c', j2='c')
					self.fade_led(state=0, fade_delay=2, background=False)

		except KeyboardInterrupt:
			self.disp_text('Program Stop', 'By KBI', j2='c')
			self.motor.stop()
			self.disp_text('Power Cycle to', 'Continue', j1='c', j2='c')
