from rpi_lcd import LCD
import RPi.GPIO as GPIO
import time
import subprocess
import datetime

# Initialize LCD
lcd = LCD()

# Set up GPIO for touch sensors
# Bạn cần kết nối các cảm biến của mình với các chân GPIO tương ứng
touch_pin_1 = 27  # ABC
touch_pin_2 = 12  # DEF
touch_pin_3 = 16  # GHI
touch_pin_4 = 13  # JKL
touch_pin_5 = 26  # MNO
touch_pin_6 = 5   # PQRS
touch_pin_7 = 14  # TUV
touch_pin_8 = 21  # WXYZ
touch_pin_d = 19  # Chữ Đ
touch_pin_enter = 20 # Enter (phát âm)
touch_pin_space = 6
touch_pin_backspace = 15
touch_pin_clear = 7

GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_d, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_enter, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_space, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_backspace, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_clear, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Dictionaries for character mapping
char_map = {
    touch_pin_1: ["a", "b", "c", "A", "B", "C"],
    touch_pin_2: ["d", "e", "f", "D", "E", "F"],
    touch_pin_3: ["g", "h", "i", "G", "H", "I"],
    touch_pin_4: ["j", "k", "l", "J", "K", "L"],
    touch_pin_5: ["m", "n", "o", "M", "N", "O"],
    touch_pin_6: ["p", "q", "r", "s", "P", "Q", "R", "S"],
    touch_pin_7: ["t", "u", "v", "T", "U", "V"],
    touch_pin_8: ["w", "x", "y", "z", "W", "X", "Y", "Z"],
    touch_pin_d: ["d", "D", "đ", "Đ"], # Phím riêng cho chữ Đ
}

telex_accents = {
    's': 'sắc',
    'f': 'huyền',
    'r': 'hỏi',
    'x': 'ngã',
    'j': 'nặng',
    'w': 'mũ',
    'a': 'trăng',
    'd': 'đ'
}

telex_vowels = {
    'a': {'s': 'á', 'f': 'à', 'r': 'ả', 'x': 'ã', 'j': 'ạ', 'w': 'â', 'a': 'ă'},
    'e': {'s': 'é', 'f': 'è', 'r': 'ẻ', 'x': 'ẽ', 'j': 'ẹ', 'w': 'ê'},
    'o': {'s': 'ó', 'f': 'ò', 'r': 'ỏ', 'x': 'õ', 'j': 'ọ', 'w': 'ô'},
    'u': {'s': 'ú', 'f': 'ù', 'r': 'ủ', 'x': 'ũ', 'j': 'ụ', 'w': 'ư'},
    'y': {'s': 'ý', 'f': 'ỳ', 'r': 'ỷ', 'x': 'ỹ', 'j': 'ỵ'},
}

# Global variables
input_string = ""
last_touch_time = time.time()
last_touched_pin = None
LCD_COLUMNS = 16

def speak_text(text):
    subprocess.call(['espeak-ng', '-v vi', text])

def update_lcd(text_to_display):
    lcd.clear()
    if len(text_to_display) > LCD_COLUMNS:
        lcd.text(text_to_display[:LCD_COLUMNS], 1)
        lcd.text(text_to_display[LCD_COLUMNS:], 2)
    else:
        lcd.text(text_to_display, 1)

# Main event handler
def on_touch(channel):
    global input_string, last_touch_time, last_touched_pin
    
    current_time = time.time()
    
    if GPIO.input(channel) == GPIO.LOW:
        # Enter key event
        if channel == touch_pin_enter:
            if input_string:
                speak_text(input_string)
                input_string = ""
                update_lcd(input_string)
            return

        # Clear key event
        if channel == touch_pin_clear:
            input_string = ""
            update_lcd(input_string)
            return
            
        # Backspace key event
        if channel == touch_pin_backspace:
            if input_string:
                input_string = input_string[:-1]
            update_lcd(input_string)
            return

        # Space key event
        if channel == touch_pin_space:
            input_string += " "
            last_touched_pin = None
            update_lcd(input_string)
            return
            
        # General character and Telex logic
        char_added = ""
        
        # Check if the touch is a Telex accent key
        if channel in telex_accents:
            if input_string:
                last_char = input_string[-1].lower()
                telex_key = telex_accents[channel]
                
                # Special case for 'đ' from 'd'
                if last_char == 'd' and telex_key == 'đ':
                    input_string = input_string[:-1] + 'đ'
                # Check for other telex accents
                elif last_char in telex_vowels and telex_key in telex_vowels[last_char]:
                    input_string = input_string[:-1] + telex_vowels[last_char][telex_key]
                else:
                    input_string += telex_key[0] # Add first letter of accent name
            else:
                input_string += telex_accents[channel][0]
            update_lcd(input_string)
            return

        # Check for a regular character keypress
        if channel in char_map:
            current_char_list = char_map[channel]
            
            # Check for consecutive press
            if (current_time - last_touch_time) < 1.0 and last_touched_pin == channel and input_string:
                if input_string[-1] in current_char_list:
                    current_index = current_char_list.index(input_string[-1])
                    next_index = (current_index + 1) % len(current_char_list)
                    input_string = input_string[:-1] + current_char_list[next_index]
                else:
                    input_string += current_char_list[0]
            else:
                input_string += current_char_list[0]
            
            last_touched_pin = channel
            last_touch_time = current_time
            update_lcd(input_string)
            
# Register events for all touch sensors
all_touch_pins = [touch_pin_1, touch_pin_2, touch_pin_3, touch_pin_4, touch_pin_5,
                  touch_pin_6, touch_pin_7, touch_pin_8, touch_pin_d,
                  touch_pin_enter, touch_pin_space, touch_pin_backspace, touch_pin_clear]

for pin in all_touch_pins:
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=on_touch, bouncetime=200)

try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
