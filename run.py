import RPi.GPIO as GPIO
import time
import subprocess
import speech_recognition as sr
from rpi_lcd import LCD
import unicodedata
import os
from gtts import gTTS
import simpleaudio as sa

# ==================== Hardware Initialization ====================
lcd = None
lcd_working = False

try:
    lcd = LCD()
    lcd_working = True
except Exception as e:
    print(f"Lỗi LCD: Không thể kết nối đến màn hình. Vui lòng kiểm tra cap kết nối. Chi tiết lỗi: {e}")
    print("Chương trình sẽ hoạt động ở chế độ dự phòng, hiển thị văn bản trên Terminal.")

# Define GPIO pins for the 9 sensors
touch_pins = {
    # 8 letter keys
    27: ['a', 'ă', 'â', 'b', 'c'],
    12: ['d', 'đ', 'e', 'ê', 'g'],
    16: ['h', 'i', 'k', 'l'],
    13: ['m', 'n', 'o', 'ô', 'ơ'],
    26: ['p', 'q', 'r', 's', 't'],
    5: ['u', 'ư', 'v', 'x', 'y'],
    14: ['z'],
    21: ['w'],
    
    # 1 multi-function key
    19: 'function_key',
}

# Configure GPIO pins
GPIO.setmode(GPIO.BCM)
for pin in touch_pins.keys():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ==================== Telex Input Logic ====================
telex_key_map = {
    # Phím tương ứng với dấu, không phải chữ cái
    26: 's',   # Phím s (sắc)
    12: 'f',  # Phím f (huyền)
    16: 'r',  # Phím r (hỏi)
    5: 'x',  # Phím x (ngã)
    13: 'j',  # Phím j (nặng)
    21: 'w',  # Phím w (mũ)
    27: 'a',  # Phím a (cho â, ă)
    14: 'd',  # Phím d (cho đ)
}

telex_rules = {
    'a': {'s': 'á', 'f': 'à', 'r': 'ả', 'x': 'ã', 'j': 'ạ', 'w': 'â', 'a': 'ă'},
    'e': {'s': 'é', 'f': 'è', 'r': 'ẻ', 'x': 'ẽ', 'j': 'ẹ', 'w': 'ê'},
    'o': {'s': 'ó', 'f': 'ò', 'r': 'ỏ', 'x': 'õ', 'j': 'ọ', 'w': 'ô', 'a': 'ơ'},
    'u': {'s': 'ú', 'f': 'ù', 'r': 'ủ', 'x': 'ũ', 'j': 'ụ', 'w': 'ư'},
    'y': {'s': 'ý', 'f': 'ỳ', 'r': 'ỷ', 'x': 'ỹ', 'j': 'ỵ'},
    'd': {'d': 'đ'}
}

# ==================== Global State Variables ====================
input_string = ""
last_touch_time = 0
last_touched_pin = None
LCD_COLUMNS = 16
function_tap_count = 0
function_last_tap_time = 0

# ==================== Utility Functions ====================
def speak_text(text):
    """Speaks the text out loud using gTTS and simpleaudio."""
    try:
        tts = gTTS(text=text, lang='vi', slow=False)
        tts.save("temp.mp3")
        wave_obj = sa.WaveObject.from_wave_file("temp.mp3")
        play_obj = wave_obj.play()
        play_obj.wait_done()
        os.remove("temp.mp3")
    except Exception as e:
        print(f"Error speaking text: {e}")
        update_lcd("Loi phat am")

def remove_accents(input_str):
    """
    Converts a Vietnamese string with accents to a string without accents
    by using a manual mapping. This is the most reliable method for LCD compatibility.
    """
    if not isinstance(input_str, str):
        return ""

    accents_mapping = {
        'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a', 'ă': 'a', 'â': 'a',
        'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e', 'ê': 'e',
        'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o', 'ô': 'o', 'ơ': 'o',
        'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u', 'ư': 'u',
        'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'đ': 'd',
        'Á': 'A', 'À': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A', 'Ă': 'A', 'Â': 'A',
        'É': 'E', 'È': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E', 'Ê': 'E',
        'Ó': 'O', 'Ò': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O', 'Ô': 'O', 'Ơ': 'O',
        'Ú': 'U', 'Ù': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U', 'Ư': 'U',
        'Ý': 'Y', 'Ỳ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
        'Đ': 'D'
    }

    result = ""
    for char in input_str:
        result += accents_mapping.get(char, char)
    return result

def update_lcd(text_to_display):
    """Updates the text on the LCD screen, handling potential encoding errors."""
    if not lcd_working:
        print(f"Terminal: {text_to_display}")
        return

    display_text = remove_accents(text_to_display)
    
    lcd.clear()
    try:
        if len(display_text) > LCD_COLUMNS:
            lcd.text(display_text[:LCD_COLUMNS], 1)
            lcd.text(display_text[LCD_COLUMNS:], 2)
        else:
            lcd.text(display_text, 1)
    except UnicodeEncodeError as e:
        print(f"UnicodeEncodeError: Cannot display '{text_to_display}'. Error: {e}")
        lcd.clear()
        lcd.text("Loi hien thi", 1)
        lcd.text("ky tu", 2)
    except Exception as e:
        print(f"Loi LCD: Khong the ket noi den man hinh. Vui long kiem tra cap ket noi. Chi tiet loi: {e}")
        # Không có gì để hiển thị trên LCD nếu không kết nối được

def listen_and_transcribe():
    """Uses the microphone to transcribe speech to text."""
    global input_string
    r = sr.Recognizer()
    update_lcd("Dang nghe...")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5)
            update_lcd("Dang xu ly...")
            text = r.recognize_google(audio, language="vi-VN")
            input_string += " " + text
            update_lcd(input_string)
        except sr.WaitTimeoutError:
            update_lcd("Het thoi gian.")
        except sr.UnknownValueError:
            update_lcd("Khong hieu ban noi gi.")
        except sr.RequestError as e:
            update_lcd(f"Loi: {e}")

def apply_telex_rule(telex_key):
    """Applies a Telex rule based on the key pressed."""
    global input_string
    
    if not input_string:
        return
    
    last_char = input_string[-1].lower()
    
    # Check if the last character is a vowel that can have a Telex mark
    if last_char in telex_rules:
        # Check if the telex rule exists for the key pressed
        if telex_key in telex_rules[last_char]:
            new_char = telex_rules[last_char][telex_key]
            input_string = input_string[:-1] + new_char
            update_lcd(input_string)
        else:
            # Handle cases where the key pressed doesn't match a rule
            # For example, pressing 's' after 'u' should not do anything.
            pass
    
def handle_character_input(channel):
    """Handles input from the character keys (multi-tap logic)."""
    global input_string, last_touch_time, last_touched_pin
    current_time = time.time()
    TAP_WINDOW = 0.5 # Window for multi-tap, in seconds
    
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
    # Thời gian chờ được đặt riêng cho phím chức năng
    FUNCTION_TAP_WINDOW = 2.0 
    
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
        update_lcd(input_string)
    elif function_tap_count == 2:
        # Tap twice: Backspace
        if input_string:
            input_string = input_string[:-1]
        update_lcd(input_string)
    elif function_tap_count == 3:
        # Tap three times: Speak the text
        speak_text(input_string)
    elif function_tap_count == 4:
        # Tap four times: Listen
        listen_and_transcribe()
        function_tap_count = 0 # Reset after the last action
    
    # For taps beyond 4, reset the counter
    if function_tap_count > 4:
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
        elif channel in telex_key_map:
            apply_telex_rule(telex_key_map[channel])
        else:
            handle_character_input(channel)

# Register event detection for all sensors on both edges (rising and falling)
# Set a bouncetime to prevent switch bounce
for pin in touch_pins.keys():
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=on_touch_event, bouncetime=50)

try:
    print("Găng tay đã sẵn sàng. Bắt đầu gõ!")
    update_lcd("San sang...")
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Dừng chương trình.")

finally:
    GPIO.cleanup()
    if lcd_working:
        lcd.clear()
