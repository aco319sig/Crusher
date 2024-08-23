from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
factory = PiGPIOFactory()
led_pin = 19
led = PWMLED(pin=led_pin, initial_value=0.2, pin_factory=factory)

def fade_led(on, duration=2, steps=25):
	start_value = led.value
	end_value = 1 if on else 0
	if not start_value == end_value:
		step_time = duration / steps
		value_change = (end_value - start_value) / steps
		for _ in range(steps):
			new_value = led.value + value_change
			led.value = max(0, min(1, new_value))
			sleep(step_time)
		led.value = end_value

def true_fade(on, fade_delay=2, steps=25, background=True):
	# on=<True=on, False=off>, fade_delay=<seconds>, background=<True=return success immediately, False=Wait until fade is complete>
	end_value = 1 if on else 0
	if led.value == end_value:
		return
	
	start_value = led.value
	if not led.value == 1 and not led.value == 0:
		start_value = led.value
		step_time = fade_delay / steps
		value_change = (end_value - start_value) / steps

		for _ in range(steps):
			new_value = led.value + value_change
			led.value = max(0, min(1, new_value))
			sleep(step_time)
	else:
		if on:
			led.blink(on_time=0, off_time=0, fade_in_time=fade_delay, fade_out_time=0, n=1, background=background)
		else:
			led.blink(on_time=0, off_time=0, fade_in_time=0, fade_out_time=fade_delay, n=1, background=background)
	
	led.value = end_value

