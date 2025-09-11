import RPi.GPIO as GPIO
import time
import subprocess
import speech_recognition as sr
from rpi_lcd import LCD
import unicodedata
import os
from gtts import gTTS
import simpleaudio as sa

# ==================== Khởi tạo phần cứng ====================
lcd = LCD()

# Định nghĩa các chân GPIO cho 9 cảm biến
touch_pins = {
    # 8 phím chữ cái
    27: ['a', 'ă', 'â', 'b', 'c'],
    12: ['d', 'đ', 'e', 'ê', 'g'],
    16: ['h', 'i', 'k', 'l'],
    13: ['m', 'n', 'o', 'ô', 'ơ'],
    26: ['p', 'q', 'r', 's', 't'],
    5: ['u', 'ư', 'v', 'x', 'y'],
    14: ['z'],
    21: ['w'],
    
    # 1 phím chức năng đa năng
    19: [' ', '<del>', '<speak>', '<listen>'],
}

# Cấu hình các chân GPIO
GPIO.setmode(GPIO.BCM)
for pin in touch_pins.keys():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ==================== Logic gõ Telex ====================
telex_key_map = {
    's': 's',   # Phím s (sắc)
    'f': 'f',  # Phím f (huyền)
    'r': 'r',  # Phím r (hỏi)
    'x': 'x',  # Phím x (ngã)
    'j': 'j',  # Phím j (nặng)
    'w': 'w',  # Phím w (mũ)
    'a': 'a',  # Phím a (cho â, ă)
    'd': 'd',  # Phím d (cho đ)
}

telex_rules = {
    'a': {'s': 'á', 'f': 'à', 'r': 'ả', 'x': 'ã', 'j': 'ạ', 'w': 'â', 'a': 'ă'},
    'e': {'s': 'é', 'f': 'è', 'r': 'ẻ', 'x': 'ẽ', 'j': 'ẹ', 'w': 'ê'},
    'o': {'s': 'ó', 'f': 'ò', 'r': 'ỏ', 'x': 'õ', 'j': 'ọ', 'w': 'ô'},
    'u': {'s': 'ú', 'f': 'ù', 'r': 'ủ', 'x': 'ũ', 'j': 'ụ', 'w': 'ư'},
    'y': {'s': 'ý', 'f': 'ỳ', 'r': 'ỷ', 'x': 'ỹ', 'j': 'ỵ'},
    'd': {'d': 'đ'}
}

# ==================== Biến trạng thái toàn cục ====================
input_string = ""
last_touch_time = 0
last_touched_pin = None
LCD_COLUMNS = 16
accent_mode = False
function_tap_count = 0
function_last_tap_time = 0
function_press_start_time = 0

# ==================== Hàm tiện ích ====================
def speak_text(text):
    """Phát âm văn bản ra loa bằng gTTS và simpleaudio."""
    try:
        tts = gTTS(text=text, lang='vi', slow=False)
        tts.save("temp.mp3")
        wave_obj = sa.WaveObject.from_wave_file("temp.mp3")
        play_obj = wave_obj.play()
        play_obj.wait_done()
        os.remove("temp.mp3")
    except Exception as e:
        print(f"Lỗi khi phát âm: {e}")
        update_lcd("Loi phat am")

def remove_accents(input_str):
    """
    Chuyển đổi chuỗi tiếng Việt có dấu thành không dấu bằng cách ánh xạ thủ công.
    Đây là phương pháp đáng tin cậy nhất để đảm bảo tương thích với màn hình LCD.
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
    """Cập nhật văn bản trên màn hình LCD."""
    display_text = remove_accents(text_to_display)
    
    lcd.clear()
    if len(display_text) > LCD_COLUMNS:
        lcd.text(display_text[:LCD_COLUMNS], 1)
        lcd.text(display_text[LCD_COLUMNS:], 2)
    else:
        lcd.text(display_text, 1)

def apply_telex_rule(accent_char):
    """Áp dụng quy tắc Telex để thêm dấu."""
    global input_string
    if not input_string:
        return
    
    last_char = input_string[-1].lower()
    
    if last_char in telex_rules:
        if accent_char in telex_rules[last_char]:
            new_char = telex_rules[last_char][accent_char]
            input_string = input_string[:-1] + new_char
            update_lcd(input_string)
            return
        
    update_lcd(input_string)

def handle_input(channel):
    """Xử lý đầu vào từ các phím gõ chữ và phím chức năng."""
    global input_string, last_touch_time, last_touched_pin, accent_mode
    current_time = time.time()
    
    key_list = touch_pins.get(channel)
    if not key_list:
        return
    
    # Logic gõ Telex
    if accent_mode:
        if isinstance(key_list, list):
            for key in key_list:
                if key in telex_key_map.values():
                    apply_telex_rule(key)
        accent_mode = False
        return

    # Logic xử lý các phím chức năng
    if channel == 19:
        if (current_time - last_touch_time) < 1.0 and last_touched_pin == channel:
            current_index = key_list.index(input_string[-1]) if input_string and input_string[-1] in key_list else -1
            next_index = (current_index + 1) % len(key_list)
            action = key_list[next_index]
        else:
            action = key_list[0]
            
        if action == ' ':
            input_string += " "
        elif action == '<del>':
            if input_string:
                input_string = input_string[:-1]
        elif action == '<speak>':
            speak_text(input_string)
        elif action == '<listen>':
            listen_and_transcribe()
            
        last_touched_pin = channel
        last_touch_time = current_time
        update_lcd(input_string)
        return

    # Logic gõ chữ và chuyển ký tự (Multi-tap)
    char_list = key_list
    if isinstance(char_list, list):
        if (current_time - last_touch_time) < 1.0 and last_touched_pin == channel and input_string:
            current_char = input_string[-1]
            try:
                current_index = char_list.index(current_char)
                next_index = (current_index + 1) % len(char_list)
                input_string = input_string[:-1] + char_list[next_index]
            except ValueError:
                input_string += char_list[0]
        else:
            input_string += char_list[0]
    else: # Ký tự đơn
        input_string += char_list

    last_touched_pin = channel
    last_touch_time = current_time
    update_lcd(input_string)


def listen_and_transcribe():
    """Sử dụng microphone để chuyển giọng nói thành văn bản."""
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

# ==================== Hàm xử lý chính ====================
def on_touch_event(channel):
    if GPIO.input(channel) == GPIO.HIGH:
        handle_input(channel)

# ==================== Vòng lặp chính ====================
# Đăng ký sự kiện cho tất cả các cảm biến với chế độ phát hiện cả hai cạnh
# Thay đổi bouncetime về 50ms để chống nảy phím hiệu quả
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
    lcd.clear()
