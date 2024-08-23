from gpiozero import PWMLED
from time import sleep

def fade_to_full(led, start_value=0.5, duration=2, steps=100):
    """
    Fade a PWMLED from a partial brightness to full brightness.
    
    Parameters:
    - led: PWMLED object
    - start_value: Initial brightness (0.0 to 1.0), default is 0.5
    - duration: Total time for the fade in seconds, default is 2
    - steps: Number of steps in the fade, default is 100
    """
    
    # Ensure start_value is between 0 and 1
    start_value = max(0, min(start_value, 1))
    
    # Calculate the step size and delay
    step_size = (1 - start_value) / steps
    delay = duration / steps
    
    # Set the initial value
    led.value = start_value
    
    # Fade to full brightness
    for _ in range(steps):
        led.value += step_size
        sleep(delay)
    
    # Ensure the LED is at full brightness
    led.value = 1