from gpiozero import Button, Motor, PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import drivers, socket, sys
from time import time as ti
from pydbus import SystemBus

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
	led_pin = 19
	"""

	def __init__(self, crush_pin=23, retract_pin=24, crush_limit=17, retract_limit=25, start_pin=16, e_stop_pin=12, lid_pin=4, led_pin=19):
		super(Robot, self).__init__()
		self.motor = Motor(crush_pin, retract_pin)
		self.c_limit = Button(crush_limit)
		self.r_limit = Button(retract_limit)
		self.start_button = Button(start_pin)
		self.estop_button = Button(e_stop_pin)
		self.lid_safe = Button(lid_pin)
		self.factory = PiGPIOFactory()
		self.led = PWMLED(pin=led_pin, initial_value=0.1, pin_factory=self.factory)
		self.lcd = drivers.Lcd()
		self.all_stop = False

	def fade_led(self, on, fade_delay=2, steps=50):
		# on=<True=on, False=off>, fade_delay=<seconds>, fade_delay / steps = frame rate
		end_value = 1 if on else 0
		if self.led.value == end_value:
			return
		
		start_value = self.led.value
		step_time = fade_delay / steps
		value_change = (end_value - start_value) / steps

		for _ in range(steps):
			new_value = self.led.value + value_change
			self.led.value = max(0, min(1, new_value))
			sleep(step_time)
		
		self.led.value = end_value


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
				elif self.all_stop:
					self.motor.stop()
					sleep(30)
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
			self.fade_led(on=True, fade_delay=2)
			while not self.lid_safe.is_pressed:
				sleep(0.25)
				if ti() > delay:
					self.disp_text(cl=False, l2='Timeout = 10 sec')
					return False
				elif self.all_stop:
					sleep(30)
					return
			self.disp_text(cl=False, l2='Lid is closed')
			self.fade_led(on=False, fade_delay=2)
			sleep(0.5)
			return True
		else:
			return True

	def _crush(self, n=31):
		if self.lid_check(10):
			if not self.c_limit.is_pressed:
				delay = ti() + n
				self.disp_text('Crushing...')
				self.fade_led(on=True, fade_delay=1)
				self.motor.forward()
				while not self.c_limit.is_pressed:
					if self.all_stop:
						self.motor.stop()
						sleep(30)
						return False
					elif ti() > delay:
						self.motor.stop()
						self.disp_text('Crush took', 'too long!')
						sleep(3)
						self.disp_text('Check for Jam!', j1='c')
						return False
					elif not self.lid_safe.is_pressed:
						self.motor.stop()
						self.disp_text('Close Lid!!')
						stop_time = str(round(delay - ti()))
						time_left = 'Timeout in: ' + stop_time + 's'
						self.disp_text(cl=False, l2=time_left)
						while not self.lid_safe.is_pressed:
							if ti() > delay:
								self.disp_text(cl=True, l1='Timed out!', l2='Re-homing...', j1='c', j2='c')
								sleep(1)
								return False
							sleep(0.5)
						self.disp_text(cl=False, l2='Lid is closed')
						delay = ti() + int(stop_time)
						sleep(0.5)
						self.disp_text(l1='Lid is closed', l2='Continuing', j2='r')
						self.motor.forward()
					sleep(0.2)
				self.motor.stop()
				self.disp_text(cl=False, l2='...Done!', j2='r')
				sleep(0.5)
				if self.home():
					self.disp_text('Press Start', 'to begin...', j1='c', j2='c')
					self.fade_led(on=False, fade_delay=2)
					return True
			else:
				self.disp_text('Crusher not set')
				sleep(0.5)
				if self.home():
					self.disp_text('Press Start', 'Again!', j1='c', j2='c')
					self.fade_led(on=False, fade_delay=2)
				else:
					self.disp_text('Check for Jam!')
					sleep(1)
					return False
		else:
			self.disp_text('Lid Must Be', 'Closed To Run')
			return False

	def reset_pi(self):
		print("Resetting...")
		self.disp_text('RESETTING...')
		sleep(5)
		bus = SystemBus()
		systemd = bus.get(".systemd1")
		systemd.RestartUnit("crusher.service", "fail")
		print("reset command sent")
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
		self.disp_text('Resetting', 'in 10 seconds', j1='c', j2='c')
		print("Emergency Stop Pressed!")
		sleep(2)
		self.fade_led(on=False, fade_delay=4)
		self.all_stop = False
		self.reset_pi()

	def cycle(self):
		if not self.r_limit.is_pressed and not self.all_stop:
			self.home()
			sleep(1)
			self.fade_led(False, fade_delay=2)
			self.disp_text('Press Start', 'to begin...', j1='c', j2='c')

		try:
			while True:
				if self.all_stop:
					sleep(30)
					return
				first = self.start_button.value
				sleep(0.05)
				second = self.start_button.value
				if first and not second:
					self.disp_text('Start Pressed')
				elif not first and second:
					self.disp_text(l2='Start released!', cl=False)
					sleep(0.3)
					if not self._crush():
						if not self.all_stop:
							self.home()
							self.disp_text('Press Start', 'to begin...', j1='c', j2='c')
							self.fade_led(on=False, fade_delay=2)
				elif not self.lid_safe.value:
					self.disp_text('Lid Open!')
					while not self.lid_safe.is_pressed:
						self.fade_led(on=True, fade_delay=2)
					self.disp_text('Press Start', 'to begin...', j1='c', j2='c')
					self.fade_led(on=False, fade_delay=2)

		except KeyboardInterrupt:
			self.disp_text('Program Stop', 'By KBI', j2='c')
			self.motor.stop()
			self.disp_text('Restart Svc', 'To Continue', j1='c', j2='c')
