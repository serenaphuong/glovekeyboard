import RPi.GPIO as GPIO
import time
import subprocess
import speech_recognition as sr
from rpi_lcd import LCD

# ==================== Hardware Initialization ====================
lcd = None
try:
    lcd = LCD()
    print("LCD screen connected successfully.")
except Exception as e:
    print(f"LCD Error: Cannot connect to screen. Please check the cable. Error details: {e}")
    lcd = None

# Define GPIO pins for the 9 sensors
touch_pins = {
    # 8 letter keys
    27: ['a', 'b', 'c'],
    12: ['d', 'e', 'f'],
    16: ['g', 'h', 'i'],
    13: ['j', 'k', 'l'],
    26: ['m', 'n', 'o'],
    5: ['p', 'q', 'r'],
    14: ['s', 't', 'u'],
    21: ['v', 'w', 'x'],
    
    # 1 multi-function key
    19: 'function_key',
}

# Configure GPIO pins
GPIO.setmode(GPIO.BCM)
for pin in touch_pins.keys():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ==================== Global State Variables ====================
input_string = ""
last_touch_time = 0
last_touched_pin = None
LCD_COLUMNS = 16
function_tap_count = 0
function_last_tap_time = 0

# ==================== Utility Functions ====================
def speak_text(text):
    """Speaks the text out loud using espeak-ng."""
    try:
        subprocess.run(['espeak-ng', '-v', 'en', text], check=True)
    except FileNotFoundError:
        error_message = "espeak-ng not found. Please install it."
        print(error_message)
        update_lcd(error_message)
    except subprocess.CalledProcessError as e:
        error_message = f"Error speaking text: {e}"
        print(error_message)
        update_lcd(error_message)

def listen_and_transcribe():
    """Listens for audio input and transcribes it to text using an offline library."""
    global input_string
    r = sr.Recognizer()
    mic = sr.Microphone()

    update_lcd("Listening...")
    print("Listening...")
    
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5)

        update_lcd("Transcribing...")
        print("Transcribing...")
        
        # Use PocketSphinx for offline transcription
        text = r.recognize_sphinx(audio, language='en-US')
        input_string += text
        update_lcd(input_string)
        print(f"You said: {text}")

    except sr.UnknownValueError:
        error_message = "Could not understand audio"
        print(error_message)
        update_lcd(error_message)
    except sr.RequestError as e:
        error_message = f"Could not request results; check your PocketSphinx installation: {e}"
        print(error_message)
        update_lcd(error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        update_lcd(error_message)

def update_lcd(text_to_display):
    """Updates the text on the LCD screen, handling potential encoding errors."""
    if lcd is None:
        print(f"Terminal: {text_to_display}")
        return

    try:
        lcd.clear()
        # Filter characters to ensure they can be displayed on the LCD
        display_text = "".join(c if 32 <= ord(c) <= 126 else ' ' for c in text_to_display)
        if len(display_text) > LCD_COLUMNS:
            lcd.text(display_text[:LCD_COLUMNS], 1)
            lcd.text(display_text[LCD_COLUMNS:], 2)
        else:
            lcd.text(display_text, 1)
    except Exception as e:
        print(f"LCD error when updating text: {e}")
        lcd.clear()
        lcd.text("Display error", 1)
        lcd.text("character", 2)

def handle_character_input(channel):
    """Handles input from the character keys (multi-tap logic)."""
    global input_string, last_touch_time, last_touched_pin
    current_time = time.time()
    TAP_WINDOW = 2.0 # Window for multi-tap, in seconds
    
    char_list = touch_pins.get(channel)
    if not char_list:
        return

    # Multi-tap logic for character selection
    if (current_time - last_touch_time) < TAP_WINDOW and last_touched_pin == channel and input_string:
        current_char = input_string[-1]
        try:
            current_index = char_list.index(current_char)
            next_index = (current_index + 1) % len(char_list)
            input_string = input_string[:-1] + char_list[next_index]
        except ValueError:
            input_string += char_list[0]
    else:
        input_string += char_list[0]

    last_touched_pin = channel
    last_touch_time = current_time
    update_lcd(input_string)

def handle_function_input(channel):
    """Handles input from the function key (multi-tap logic for actions)."""
    global input_string, function_tap_count, function_last_tap_time
    current_time = time.time()
    FUNCTION_TAP_WINDOW = 4.0
    
    # Check if this tap is part of the same sequence
    if (current_time - function_last_tap_time) > FUNCTION_TAP_WINDOW:
        function_tap_count = 1
    else:
        function_tap_count += 1
    
    function_last_tap_time = current_time

    # Execute action based on tap count
    if function_tap_count == 1:
        # Tap once: Add a space
        input_string += " "
    elif function_tap_count == 2:
        # Tap twice: Backspace
        if input_string:
            input_string = input_string[:-1]
    elif function_tap_count == 3:
        # Tap three times: Speak the text
        speak_text(input_string)
    elif function_tap_count == 4:
        # Tap four times: Speech-to-Text
        listen_and_transcribe()
    elif function_tap_count == 5:
        # Tap five times: Clear all
        input_string = ""
    
    update_lcd(input_string)
    
    # For taps beyond 5, reset the counter
    if function_tap_count > 5:
        function_tap_count = 0


# ==================== Main Event Loop ====================
def on_touch_event(channel):
    """
    Main callback function triggered by GPIO events.
    Handles key release (rising edge) to prevent multiple triggers.
    """
    # Only process on key release to handle debounce
    if GPIO.input(channel) == GPIO.HIGH:
        if touch_pins.get(channel) == 'function_key':
            handle_function_input(channel)
        else:
            handle_character_input(channel)

# Register event detection for all sensors on both edges (rising and falling)
# Set a bouncetime to prevent switch bounce
for pin in touch_pins.keys():
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=on_touch_event, bouncetime=50)

try:
    print("Glove is ready. Start typing!")
    update_lcd("Ready...")
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping the program.")

finally:
    GPIO.cleanup()
    if lcd:
        try:
            lcd.clear()
        except Exception as e:
            print(f"Error cleaning up LCD screen: {e}")
