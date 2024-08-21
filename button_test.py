#!/usr/bin/env python3

# from gpiozero import DigitalOutputDevice as DOD
# crush_motor = DOD(23, active_high=True, initial_value=False)
# retract_motor = DOD(24, active_high=True, initial_value=False)

from time import sleep
from gpiozero import Button, PWMLED, Motor

crush_motor = Motor(forward=23, backward=24)
crush_limit = Button(17)
retract_limit = Button(25)
lid_safety = Button(4)
start_button = Button(16)
e_stop = Button(12)
led = PWMLED(26)
disp_sda = 2
disp_scl = 3

def crush_motor_test():
	if not crush_limit.is_pressed:
		crush_motor.forward()
		sleep(0.5)
		crush_motor.stop()
		return True
	else:
		print("Crush arm is already at full extension!")
		return False

def retract_motor_test():
	if not retract_limit.is_pressed:
		crush_motor.backward()
		sleep(2)
		crush_motor.stop()
		return True
	else:
		print("Crush arm is already at full extension!")
		return False

def switch_test():
	try:
		while True:
			if retract_limit.is_pressed:
				print("retract_limit Pressed")
				led.blink(on_time=0.2, off_time=0.2, background=True)
				sleep(2)
				led.off()
			elif crush_limit.is_pressed:
				print("crush_limit Pressed")
				led.blink(on_time=0.2, off_time=0.5, background=True)
				sleep(2)
				led.off()
			elif lid_safety.is_pressed:
				print("lid_safety Pressed")
				led.blink(on_time=0.5, off_time=0.2, background=True)
				sleep(2)
				led.off()
			elif start_button.is_pressed:
				print("start_button Pressed")
				led.blink(on_time=0.5, off_time=0.5, background=True)
				sleep(2)
				led.off()
			elif e_stop.is_pressed:
				print("e_stop Pressed")
				led.blink(on_time=0.1, off_time=0.1, background=True)
				sleep(2)
				led.off()
	except KeyboardInterrupt:
		# If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
		print("Cleaning up!")
		sleep(3)

def fade_led(state, fade_delay=2, background=True):
	# state=<desired end-state of LED>, fade_delay=<seconds>, background=<True=return success immediately, False=Wait until fade is complete>
	if state == 1:
		if led.is_lit:
			pass
		else:
			led.blink(on_time=0, off_time=0, fade_in_time=fade_delay, fade_out_time=0, n=1, background=background)
			led.on()
	elif state == 0:
		if not led.is_lit:
			pass
		else:
			led.blink(on_time=0, off_time=0, fade_in_time=0, fade_out_time=fade_delay, n=1, background=background)
    
# print("Starting Test")
# sleep(2)
# print("Ready!")
# if crush_motor_test():
# 	if retract_motor_test():
# 		switch_test()
# 	else:
# 		print("See Error above:")
# else:
# 	print("See Error above:")

