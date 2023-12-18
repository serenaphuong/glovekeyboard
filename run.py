from rpi_lcd import LCD
import RPi.GPIO as GPIO
import time
import subprocess

# Initialize LCD
lcd = LCD()

# Set up GPIO for touch sensors
touch_pin_1 = 27
touch_pin_2 = 12
touch_pin_clear = 7
touch_pin_3 = 16
touch_pin_4 = 13
touch_pin_5 = 26
touch_pin_6 = 5
touch_pin_7 = 14
touch_pin_8 = 21
touch_pin_9 = 19
touch_pin_space = 6  # New touch sensor on GPIO pin 6 for space
touch_pin_backspace = 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_clear, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_space, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_backspace, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Counters for touch events
touch_count_1 = 0
touch_count_2 = 0
touch_count_clear = 0
touch_count_3 = 0
touch_count_4 = 0
touch_count_5 = 0
touch_count_6 = 0
touch_count_7 = 0
touch_count_8 = 0
touch_count_9 = 0
touch_count_space = 0
touch_count_backspace = 0

# String to store characters
input_string = ""

# LCD columns
LCD_COLUMNS = 16

def on_touch_1(channel):
    global touch_count_1
    if GPIO.input(touch_pin_1) == GPIO.LOW:
        touch_count_1 += 1

def on_touch_2(channel):
    global touch_count_2
    if GPIO.input(touch_pin_2) == GPIO.LOW:
        touch_count_2 += 1

def on_touch_clear(channel):
    global touch_count_clear
    if GPIO.input(touch_pin_clear) == GPIO.LOW:
        touch_count_clear += 1

def on_touch_3(channel):
    global touch_count_3
    if GPIO.input(touch_pin_3) == GPIO.LOW:
        touch_count_3 += 1

def on_touch_4(channel):
    global touch_count_4
    if GPIO.input(touch_pin_4) == GPIO.LOW:
        touch_count_4 += 1

def on_touch_5(channel):
    global touch_count_5
    if GPIO.input(touch_pin_5) == GPIO.LOW:
        touch_count_5 += 1

def on_touch_6(channel):
    global touch_count_6
    if GPIO.input(touch_pin_6) == GPIO.LOW:
        touch_count_6 += 1

def on_touch_7(channel):
    global touch_count_7
    if GPIO.input(touch_pin_7) == GPIO.LOW:
        touch_count_7 += 1

def on_touch_8(channel):
    global touch_count_8
    if GPIO.input(touch_pin_8) == GPIO.LOW:
        touch_count_8 += 1

def on_touch_9(channel):
    global touch_count_9
    if GPIO.input(touch_pin_9) == GPIO.LOW:
        touch_count_9 += 1

def on_touch_space(channel):
    global touch_count_space
    if GPIO.input(touch_pin_space) == GPIO.LOW:
        touch_count_space += 1
        
def speak_text(text):
    subprocess.call(['espeak-ng', text])

def on_touch_backspace(channel):
    global touch_count_backspace
    if GPIO.input(touch_pin_backspace) == GPIO.LOW:
        touch_count_backspace += 1

# Register events for touch sensors
GPIO.add_event_detect(touch_pin_1, GPIO.BOTH, callback=on_touch_1, bouncetime=100)
GPIO.add_event_detect(touch_pin_2, GPIO.BOTH, callback=on_touch_2, bouncetime=100)
GPIO.add_event_detect(touch_pin_clear, GPIO.BOTH, callback=on_touch_clear, bouncetime=100)
GPIO.add_event_detect(touch_pin_3, GPIO.BOTH, callback=on_touch_3, bouncetime=100)
GPIO.add_event_detect(touch_pin_4, GPIO.BOTH, callback=on_touch_4, bouncetime=100)
GPIO.add_event_detect(touch_pin_5, GPIO.BOTH, callback=on_touch_5, bouncetime=100)
GPIO.add_event_detect(touch_pin_6, GPIO.BOTH, callback=on_touch_6, bouncetime=100)
GPIO.add_event_detect(touch_pin_7, GPIO.BOTH, callback=on_touch_7, bouncetime=100)
GPIO.add_event_detect(touch_pin_8, GPIO.BOTH, callback=on_touch_8, bouncetime=100)
GPIO.add_event_detect(touch_pin_9, GPIO.BOTH, callback=on_touch_9, bouncetime=100)
GPIO.add_event_detect(touch_pin_space, GPIO.BOTH, callback=on_touch_space, bouncetime=100)
GPIO.add_event_detect(touch_pin_backspace, GPIO.BOTH, callback=on_touch_backspace, bouncetime=100)


try:
    while True:
        time.sleep(1.7)  # Wait for 1.8 seconds to count touch events

        if touch_count_1 == 1:
            input_string += "A"
        elif touch_count_1 == 2:
            input_string += "B"
        elif touch_count_1 == 3:
            input_string += "C"
        elif touch_count_2 == 1:
            input_string += "D"
        elif touch_count_2 == 2:
            input_string += "E"
        elif touch_count_2 == 3:
            input_string += "F"
        elif touch_count_3 == 1:
            input_string += "G"
        elif touch_count_3 == 2:
            input_string += "H"
        elif touch_count_3 == 3:
            input_string += "I"
        elif touch_count_4 == 1:
            input_string += "J"
        elif touch_count_4 == 2:
            input_string += "K"
        elif touch_count_4 == 3:
            input_string += "L"
        elif touch_count_5 == 1:
            input_string += "M"
        elif touch_count_5 == 2:
            input_string += "N"
        elif touch_count_5 == 3:
            input_string += "O"
        elif touch_count_6 == 1:
            input_string += "P"
        elif touch_count_6 == 2:
            input_string += "Q"
        elif touch_count_6 == 3:
            input_string += "R"
        elif touch_count_7 == 1:
            input_string += "S"
        elif touch_count_7 == 2:
            input_string += "T"
        elif touch_count_7 == 3:
            input_string += "U"
        elif touch_count_8 == 1:
            input_string += "V"
        elif touch_count_8 == 2:
            input_string += "W"
        elif touch_count_8 == 3:
            input_string += "X"
        elif touch_count_9 == 1:
            input_string += "Y"
        elif touch_count_9 == 2:
            input_string += "Z"
        elif touch_count_space == 1:
            input_string += " "  # Space character
            
        if touch_count_backspace == 1 and len(input_string) > 0:
            input_string = input_string[:-1]

        # Check if the clear touch sensor is pressed
        if touch_count_clear == 1:
            input_string = ""  # Clear the input string
            lcd.clear()  # Clear the LCD display

        # Display the string on the LCD
        lcd.text(input_string[:LCD_COLUMNS], 1)  # Display on the first line

        # Check if the length of the string exceeds the LCD width
        if len(input_string) > LCD_COLUMNS:
            lcd.text(input_string[LCD_COLUMNS:], 2)  # Display on the second line

        # Reset touch event counters
        touch_count_1 = 0
        touch_count_2 = 0
        touch_count_clear = 0
        touch_count_3 = 0
        touch_count_4 = 0
        touch_count_5 = 0
        touch_count_6 = 0
        touch_count_7 = 0
        touch_count_8 = 0
        touch_count_9 = 0
        touch_count_space = 0
        touch_count_backspace = 0
        if input_string:
            speak_text(input_string)

except KeyboardInterrupt:
    pass

finally:
    # Clean up GPIO when the program ends
    GPIO.cleanup()




    