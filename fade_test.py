from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
factory = PiGPIOFactory()
led_pin = 19
led = PWMLED(pin=led_pin, initial_value=0.2, pin_factory=factory)

def fade_led(led, on=True, duration=2, steps=25):
    """
    Fade a PWMLED to either full brightness or off.
    
    :param led: PWMLED object
    :param on: Boolean, True to fade to full brightness, False to fade to off
    :param duration: Total duration of the fade in seconds (default 1 second)
    :param steps: Number of steps in the fade (default 100)
    """
    start_value = led.value
    end_value = 1 if on else 0
    
    step_time = duration / steps
    value_change = (end_value - start_value) / steps
    
    for _ in range(steps):
        new_value = led.value + value_change
        led.value += value_change
        led.value = max(0, min(1, new_value))
        sleep(step_time)
    
    # Ensure final value is exactly what we want
    led.value = end_value

