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
LED_COUNT_PER_STRIP = 60  
LED_COUNT_TOTAL = 120     
LED_PIN_1 = 18            
LED_PIN_2 = 5           
LED_FREQ_HZ = 800000     
LED_DMA = 10              
LED_BRIGHTNESS = 50      
LED_INVERT = False        
LED_CHANNEL_1 = 0         
LED_CHANNEL_2 = 1       

# Basic Color Definitions
RED_COLOR = Color(255, 0, 0)
YELLOW_COLOR = Color(255, 200, 0)
BLUE_COLOR = Color(0, 0, 255)
GREEN_COLOR = Color(0, 255, 0)
OFF_COLOR = Color(0, 0, 0)

# Zone Definitions (each zone 30 LEDs - 15 from each strip)
ZONE_SIZE = 30  
ZONES = {
    'red': (0, ZONE_SIZE),                    # 0-29 
    'yellow': (ZONE_SIZE, ZONE_SIZE * 2),     # 30-59
    'blue': (ZONE_SIZE * 2, ZONE_SIZE * 3),   # 60-89
    'green': (ZONE_SIZE * 3, ZONE_SIZE * 4)   # 90-119
}

# Create LED strip objects
strip1 = None  # GPIO18
strip2 = None  # GPIO23
if IS_RPI_ENV:
    # Initialize the first light strip (GPIO18)
    strip1 = PixelStrip(LED_COUNT_PER_STRIP, LED_PIN_1, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL_1)
    strip1.begin()
    
    # Initialize the second light strip (GPIO23)
    strip2 = PixelStrip(LED_COUNT_PER_STRIP, LED_PIN_2, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL_2)
    strip2.begin()
    
    print("Two LED light strips have been initialized on the Raspberry PI.")
    print(f"灯带1: GPIO{LED_PIN_1}, 通道{LED_CHANNEL_1}, {LED_COUNT_PER_STRIP}盏灯")
    print(f"灯带2: GPIO{LED_PIN_2}, 通道{LED_CHANNEL_2}, {LED_COUNT_PER_STRIP}盏灯")
    print(f"总计: {LED_COUNT_TOTAL}盏灯")
else:
    print("The LED light strip is not initialized (not in the Raspberry PI environment).")

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

def set_led_color(led_index, color):
    """
    Set the color of the specified LED.
    Parameter:
        led_index (int): LED索引 (0-119)
        color:
    """
    if not IS_RPI_ENV:
        return
    
    if led_index < LED_COUNT_PER_STRIP:
        # The first light strip (0-59)
        strip1.setPixelColor(led_index, color)
    else:
        # The second light strip (60-119)
        strip2.setPixelColor(led_index - LED_COUNT_PER_STRIP, color)

def show_all_strips():
    """Display the changes of all the light strips."""
    if not IS_RPI_ENV:
        return
    
    strip1.show()
    strip2.show()

def light_zone(zone_name, duration=0.8):
    """
    Light up the designated LED area and keep it on for a period of time.
    Parameter:
        zone_name (str): ('red', 'yellow', 'blue', 'green')。
        duration (float): The time when the area remains lit, measured in seconds.
    """
    color = get_color_object(zone_name)
    if not IS_RPI_ENV:
        print(f"模拟LED: 点亮区域 {zone_name}，颜色 {color}，持续 {duration} 秒")
        time.sleep(duration)
        return

    if zone_name not in ZONES:
        print(f"错误: 区域 '{zone_name}' 未定义。")
        return

    start, end = ZONES[zone_name]
    print(f"点亮区域 {zone_name}: LED {start} 到 {end-1}")
    
    # Set the colors of all the leds in this area
    for i in range(start, end):
        set_led_color(i, color)
    
    # Display changes
    show_all_strips()
    time.sleep(duration)

def turn_off_zone(zone_name):
    """
    Turn off the designated LED area.
    Parameter:
        zone_name (str): 
    """
    if not IS_RPI_ENV:
        print(f"模拟LED: 关闭区域 {zone_name}")
        return

    if zone_name not in ZONES:
        print(f"错误: 区域 '{zone_name}' 未定义。")
        return

    start, end = ZONES[zone_name]
    print(f"关闭区域 {zone_name}: LED {start} 到 {end-1}")
    
    # Set all the leds in this area to the off state
    for i in range(start, end):
        set_led_color(i, OFF_COLOR)
    
    show_all_strips()

def turn_off_all_leds():
    """Turn off all the leds on all the light strips."""
    if not IS_RPI_ENV:
        print("模拟LED: 关闭所有LED。")
        return
    
    # Turn off all the leds of the first light strip
    for i in range(LED_COUNT_PER_STRIP):
        strip1.setPixelColor(i, OFF_COLOR)
    
    # Turn off all the leds of the second light strip
    for i in range(LED_COUNT_PER_STRIP):
        strip2.setPixelColor(i, OFF_COLOR)
    
    # Display changes
    show_all_strips()
    print("所有LED已关闭。")

def play_sequence(sequence, light_duration_per_color=0.8, off_duration_between_colors=0.2):
    print(f"播放LED序列: {sequence}")
    for color_name in sequence:
        light_zone(color_name, light_duration_per_color)
        turn_off_zone(color_name)
        time.sleep(off_duration_between_colors) 

    turn_off_all_leds()
    print("LED序列播放完成。")

def test_all_zones():
    print("开始测试所有LED区域...")
    test_colors = ['red', 'yellow', 'blue', 'green']
    
    for color in test_colors:
        print(f"测试 {color} 区域...")
        light_zone(color, 1.0) 
        turn_off_zone(color)
        time.sleep(0.5) 
    
    print("LED区域测试完成。")

# Call turn_off_all_leds when the module is imported or script exits
# This ensures LEDs are off when the application stops

# import atexit
# if IS_RPI_ENV:
#     atexit.register(turn_off_all_leds)