#!/usr/bin/env python3

from time import sleep
import robot as R
"""
Expected Values:
crush_motor = Motor(forward=23, backward=24)
crush_limit = Button(17)
retract_limit = Button(25)
lid_safety = Button(4)
start_button = Button(16)
e_stop = Button(12)
disp_sda = 2 <-- auto-detected
disp_scl = 3 <-- auto-detected
"""

motor_fwd_pin = 23
motor_rev_pin = 24
c_l_pin = 17
r_l_pin = 25
l_pin = 4
s_pin = 16
e_pin = 12
led_p = 26


def main():
	HAL = R.Robot(crush_pin=motor_fwd_pin, retract_pin=motor_rev_pin, crush_limit=c_l_pin, retract_limit=r_l_pin, start_pin=s_pin, e_stop_pin=e_pin, lid_pin=l_pin, led_pin=led_p)
	HAL.disp_text('POST Complete')
	sleep(1)
	host_ip = HAL.get_ip()
	HAL.disp_text('Host IP:', str(host_ip), j1='c', j2='c')
	HAL.estop_button.when_pressed = HAL.e_stop
	sleep(5)

	if HAL.crush_motor_test():
		if not HAL.retract_motor_test():
			HAL.disp_text(l1='ERROR', j1='c', l2='COULD NOT HOME!')
	if not HAL.home():
		HAL.disp_text(l1='ERROR', j1='c', l2='COULD NOT HOME!')
		n = 10
		while n > 0:
			HAL.disp_text(cl=False, bkon=False)
			sleep(0.3)
			HAL.disp_text(cl=False)
			sleep(0.3)
			n = n - 1
		sleep(2)
		HAL.disp_text('Power cycle', 'to reset')
	else:
		HAL.disp_text('Press Start', 'to begin...', j1='c', j2='c')
		HAL.cycle()

if __name__ == "__main__":
	main()