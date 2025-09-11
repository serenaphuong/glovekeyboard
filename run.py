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
    # 8 phím chữ cái (kiểu bàn phím điện thoại cũ)
    27: ['a', 'b', 'c'],
    12: ['d', 'e', 'f'],
    16: ['g', 'h', 'i'],
    13: ['j', 'k', 'l'],
    26: ['m', 'n', 'o'],
    5: ['p', 'q', 'r', 's'],
    14: ['t', 'u', 'v'],
    21: ['w', 'x', 'y', 'z'],
    
    # 1 phím chức năng đa năng
    19: 'function_key',
}

# Cấu hình các chân GPIO
GPIO.setmode(GPIO.BCM)
for pin in touch_pins.keys():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ==================== Logic gõ Telex ====================
telex_key_map = {
    5: 's',   # Phím s (sắc)
    12: 'f',  # Phím f (huyền)
    16: 'r',  # Phím r (hỏi)
    13: 'x',  # Phím x (ngã)
    26: 'j',  # Phím j (nặng)
    21: 'w',  # Phím w (mũ)
    27: 'a',  # Phím a (cho â, ă)
    14: 'd',  # Phím d (cho đ)
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
    Chuyển đổi chuỗi tiếng Việt có dấu thành không dấu bằng cách thay thế trực tiếp
    để đảm bảo tương thích với màn hình LCD.
    """
    vietnamese_map = {
        'a': 'aàảãáạăằẳẵắặâầẩẫấậ',
        'e': 'eèẻẽéẹêềểễếệ',
        'i': 'iìỉĩíị',
        'o': 'oòỏõóọôồổỗốộơờởỡớợ',
        'u': 'uùủũúụưừửữứự',
        'y': 'yỳỷỹýỵ',
        'd': 'dđ'
    }
    
    result = ""
    for char in input_str:
        found = False
        for replacement_char, accented_chars in vietnamese_map.items():
            if char.lower() in accented_chars:
                result += replacement_char if char.islower() else replacement_char.upper()
                found = True
                break
        if not found:
            result += char
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

def handle_character_input(channel):
    """Xử lý đầu vào từ các phím gõ chữ và Telex."""
    global input_string, last_touch_time, last_touched_pin, accent_mode
    current_time = time.time()
    
    if accent_mode:
        accent_char = telex_key_map.get(channel)
        if accent_char:
            apply_telex_rule(accent_char)
        accent_mode = False
        return

    char_list = touch_pins[channel]
    
    # Kiểm tra xem đây có phải là một cú chạm liên tiếp trên cùng một phím trong vòng 2.0 giây không.
    if (current_time - last_touch_time) < 2.0 and last_touched_pin == channel and input_string:
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
    global input_string, accent_mode, last_touched_pin, function_tap_count, function_last_tap_time, function_press_start_time

    # Xử lý khi chạm vào cảm biến (Falling Edge)
    if GPIO.input(channel) == GPIO.LOW:
        if touch_pins.get(channel) == 'function_key':
            function_press_start_time = time.time()
    
    # Xử lý khi nhả tay khỏi cảm biến (Rising Edge)
    if GPIO.input(channel) == GPIO.HIGH:
        pin_function = touch_pins.get(channel)
        
        if pin_function == 'function_key':
            press_duration = time.time() - function_press_start_time
            if press_duration < 3.0: # Xử lý các lần nhấn ngắn
                current_time = time.time()
                if (current_time - function_last_tap_time) > 0.5:
                    function_tap_count = 0
                
                function_tap_count += 1
                function_last_tap_time = current_time
                
                if function_tap_count == 1:
                    # Nhấn 1 lần: Đọc văn bản
                    speak_text(input_string)
                elif function_tap_count == 2:
                    # Nhấn 2 lần: Phím cách
                    input_string += " "
                    update_lcd(input_string)
                elif function_tap_count == 3:
                    # Nhấn 3 lần: Xóa lùi
                    if input_string:
                        input_string = input_string[:-1]
                    update_lcd(input_string)
                elif function_tap_count == 4:
                    # Nhấn 4 lần: Nghe và chuyển giọng nói thành văn bản
                    listen_and_transcribe()
                    function_tap_count = 0 
                elif function_tap_count > 4:
                    function_tap_count = 0 
        else:
            handle_character_input(channel)

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
