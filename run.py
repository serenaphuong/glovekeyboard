import RPi.GPIO as GPIO
import time
import subprocess
import speech_recognition as sr
from rpi_lcd import LCD

# Khởi tạo LCD
lcd = LCD()

# Định nghĩa các chân GPIO cho 12 cảm biến
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
    
    # 4 phím chức năng
    19: 'accent',    # Phím gõ dấu (chuyển sang chế độ Telex)
    20: 'enter_or_listen',     # Phát âm văn bản hoặc Chuyển giọng nói thành văn bản
    6: 'space',      # Phím cách
    15: 'backspace', # Xóa lùi
}

# Cấu hình các chân GPIO
GPIO.setmode(GPIO.BCM)
for pin in touch_pins.keys():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Ánh xạ các phím chữ cái với các phím gõ Telex
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

# Bảng quy tắc Telex đầy đủ
telex_rules = {
    'a': {'s': 'á', 'f': 'à', 'r': 'ả', 'x': 'ã', 'j': 'ạ', 'w': 'â', 'a': 'ă'},
    'e': {'s': 'é', 'f': 'è', 'r': 'ẻ', 'x': 'ẽ', 'j': 'ẹ', 'w': 'ê'},
    'o': {'s': 'ó', 'f': 'ò', 'r': 'ỏ', 'x': 'õ', 'j': 'ọ', 'w': 'ô'},
    'u': {'s': 'ú', 'f': 'ù', 'r': 'ủ', 'x': 'ũ', 'j': 'ụ', 'w': 'ư'},
    'y': {'s': 'ý', 'f': 'ỳ', 'r': 'ỷ', 'x': 'ỹ', 'j': 'ỵ'},
    'd': {'d': 'đ'}
}

# Biến toàn cục để theo dõi trạng thái chương trình
input_string = ""
last_touch_time = 0
last_touched_pin = None
LCD_COLUMNS = 16
accent_mode = False
enter_press_start_time = 0

def speak_text(text):
    """Phát âm văn bản ra loa."""
    subprocess.call(['espeak-ng', '-v vi', text])

def update_lcd(text_to_display):
    """Cập nhật văn bản trên màn hình LCD."""
    lcd.clear()
    if len(text_to_display) > LCD_COLUMNS:
        lcd.text(text_to_display[:LCD_COLUMNS], 1)
        lcd.text(text_to_display[LCD_COLUMNS:], 2)
    else:
        lcd.text(text_to_display, 1)

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
    """Xử lý đầu vào từ các phím gõ chữ và Telex."""
    global input_string, last_touch_time, last_touched_pin, accent_mode
    current_time = time.time()
    
    # Nếu đang ở chế độ gõ dấu Telex, xử lý phím gõ dấu
    if accent_mode:
        accent_char = telex_key_map.get(channel)
        if accent_char:
            apply_telex_rule(accent_char)
        accent_mode = False
        return

    # Xử lý gõ chữ multi-tap
    char_list = touch_pins[channel]
    
    if (current_time - last_touch_time) < 0.5 and last_touched_pin == channel and input_string:
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
    update_lcd("Đang nghe...")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5)
            update_lcd("Đang xử lý...")
            text = r.recognize_google(audio, language="vi-VN")
            input_string += " " + text
            update_lcd(input_string)
        except sr.WaitTimeoutError:
            update_lcd("Hết thời gian.")
        except sr.UnknownValueError:
            update_lcd("Không hiểu bạn nói gì.")
        except sr.RequestError as e:
            update_lcd(f"Lỗi: {e}")

# Main event handler
def on_touch_down(channel):
    global enter_press_start_time
    if GPIO.input(channel) == GPIO.LOW:
        if touch_pins.get(channel) == 'enter_or_listen':
            enter_press_start_time = time.time()

def on_touch_up(channel):
    global input_string, accent_mode, enter_press_start_time
    if GPIO.input(channel) == GPIO.HIGH:
        pin_function = touch_pins.get(channel)
        
        if pin_function == 'enter_or_listen':
            press_duration = time.time() - enter_press_start_time
            if press_duration > 1.0:
                # Long press for listen functionality
                listen_and_transcribe()
            else:
                # Short press for speak functionality
                if input_string:
                    speak_text(input_string)
                    input_string = ""
                    update_lcd("Đang phát âm...")
                    time.sleep(1.5)
                    update_lcd("")
        elif pin_function == 'space':
            input_string += " "
            update_lcd(input_string)
        elif pin_function == 'backspace':
            if input_string:
                input_string = input_string[:-1]
            update_lcd(input_string)
        elif pin_function == 'accent':
            accent_mode = True
            update_lcd("Chọn dấu...")
        else:
            handle_input(channel)

# Đăng ký sự kiện cho tất cả các cảm biến
for pin in touch_pins.keys():
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=on_touch_down, bouncetime=10)
    GPIO.add_event_detect(pin, GPIO.RISING, callback=on_touch_up, bouncetime=10)

try:
    print("Găng tay đã sẵn sàng. Bắt đầu gõ!")
    update_lcd("Sẵn sàng...")
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Dừng chương trình.")

finally:
    GPIO.cleanup()
    lcd.clear()
