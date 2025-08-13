import time

# Attempt to import rpi_ws281x for LED control.
# If not on a Raspberry Pi, a dummy class will be used.
try:
    from rpi_ws281x import PixelStrip, Color
    print("rpi_ws281x imported successfully.")
    IS_RPI_ENV = True
except ImportError:
    print("rpi_ws281x not found. Running in non-Raspberry Pi environment. LED control will be simulated.")
    IS_RPI_ENV = False

    # Dummy classes for non-Raspberry Pi environment
    class Color:
        def __init__(self, r, g, b):
            pass

    class PixelStrip:
        def __init__(self, *args, **kwargs):
            pass
        def begin(self):
            pass
        def setPixelColor(self, index, color):
            pass
        def show(self):
            pass

# --- LED Configuration ---
LED_COUNT = 120
LED_PIN = 18 
LED_FREQ_HZ = 800000
LED_DMA = 10      
LED_BRIGHTNESS = 50 
LED_INVERT = False
LED_CHANNEL = 0

# Basic Color Definitions
RED_COLOR = Color(255, 0, 0)
YELLOW_COLOR = Color(255, 200, 0)
BLUE_COLOR = Color(0, 0, 255)
GREEN_COLOR = Color(0, 255, 0)
OFF_COLOR = Color(0, 0, 0)

# Zone Definitions (each zone 30 LEDs)
ZONE_SIZE = 30
ZONES = {
    'red': (0, ZONE_SIZE),           
    'yellow': (ZONE_SIZE, ZONE_SIZE * 2),   
    'blue': (ZONE_SIZE * 2, ZONE_SIZE * 3), 
    'green': (ZONE_SIZE * 3, ZONE_SIZE * 4) 
}

# Create LED strip object
strip = None
if IS_RPI_ENV:
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    print("LED strip initialized on Raspberry Pi.")
else:
    print("LED strip not initialized (not on Raspberry Pi).")

# --- LED Control Functions ---
def get_color_object(color_name):
    """Return the color object based on the color name."""
    colors = {
        'red': RED_COLOR,
        'yellow': YELLOW_COLOR,
        'blue': BLUE_COLOR,
        'green': GREEN_COLOR
    }
    return colors.get(color_name, OFF_COLOR)

def light_zone(zone_name, duration=0.8):
    """
    Light up the designated LED area and keep it on for a period of time.
    Parameter:
        zone_name (str): ('red', 'yellow', 'blue', 'green')。
        duration (float): The time when the area remains lit, measured in seconds.
    """
    color = get_color_object(zone_name)
    if not IS_RPI_ENV:
        print(f"模拟LED: {zone_name}， {color}， {duration} ")
        time.sleep(duration)
        return

    if zone_name not in ZONES:
        print(f"错误:'{zone_name}'")
        return

    start, end = ZONES[zone_name]
    for i in range(start, end):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(duration)

def turn_off_zone(zone_name):
    """
    Turn off the designated LED area.
    Parameter:
        zone_name (str):
    """
    if not IS_RPI_ENV:
        print(f"模拟LED: {zone_name}")
        return

    if zone_name not in ZONES:
        print(f"错误:'{zone_name}'")
        return

    start, end = ZONES[zone_name]
    for i in range(start, end):
        strip.setPixelColor(i, OFF_COLOR)
    strip.show()

def turn_off_all_leds():
    """Turn off all the leds on the light strip."""
    if not IS_RPI_ENV:
        print("Simulated LED: Turn off all LEDs.")
        return
    for i in range(LED_COUNT):
        strip.setPixelColor(i, OFF_COLOR)
    strip.show()
    print("All LEDs have been turned off.")

def play_sequence(sequence, light_duration_per_color=0.8, off_duration_between_colors=0.2):
    """
    Play the color sequence on the LED light strip.
    For each color in the sequence, it will light up the corresponding area,
    Then close the area and have a brief pause between the two.
    Finally, it ensures that all the leds have been turned off.

    Parameter:
        sequence (list): (For example, ['red', 'blue', 'yellow'])。
        light_duration_per_color (float): 每个LED区域保持点亮的时间 (秒)。
        off_duration_between_colors (float): 关闭一个区域与点亮序列中下一个区域之间的时间 (秒)。
    """
    print(f"Play LED sequence: {sequence}")
    for color_name in sequence:
        light_zone(color_name, light_duration_per_color)
        turn_off_zone(color_name)
        time.sleep(off_duration_between_colors)

    turn_off_all_leds() 
    print("The LED sequence playback is complete.")


# Call turn_off_all_leds when the module is imported or script exits
# This ensures LEDs are off when the application stops

# import atexit
# if IS_RPI_ENV:
#     atexit.register(turn_off_all_leds)