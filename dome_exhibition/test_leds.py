#!/usr/bin/env python3
"""
LED hardware test script
Used to verify whether the connections of 120 LED light strips are correct
"""

import time
import led_controller

def main():
    print("=== LED hardware testing program ===")
    print("This program will test all 120 LED light strips")
    print("Press Ctrl+C to stop the test")
    print()
    
    try:
        print("1. Turn off all LEDs...")
        led_controller.turn_off_all_leds()
        time.sleep(1)
        
        print("2. Test each color area...")
        led_controller.test_all_zones()
        
        print("3. Test sequence playback...")
        test_sequence = ['red', 'yellow', 'blue', 'green', 'red', 'blue']
        led_controller.play_sequence(test_sequence, 0.5, 0.3)
        
        print("4. Test the lighting of a single area...")
        colors = ['red', 'yellow', 'blue', 'green']
        for color in colors:
            print(f"Light up the {color} area...")
            led_controller.light_zone(color, 2.0)
            led_controller.turn_off_zone(color)
            time.sleep(1)
        
        print("5. Finally, turn off all the leds...")
        led_controller.turn_off_all_leds()
        
        print("Test completed!")
        
    except KeyboardInterrupt:
        print("The test was interrupted by the user")
        led_controller.turn_off_all_leds()
        print("All LEDs have been turned off")
    except Exception as e:
        print(f"An error occurred during the test: {e}")
        led_controller.turn_off_all_leds()

if __name__ == "__main__":
    main() 
