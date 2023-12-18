## Tổng quan
Dự án được thực hiện trên mạch vi điều khiển Raspberry Pi 3 Model B+, cho phép người dùng nhập văn bản bằng các mô-đun cảm biến chạm điện dung, chuyển đổi văn bản thành giọng nói và nhận diện giọng nói để hiển thị nó trên một màn hình LCD.

## Yêu cầu phần cứng
- Raspberry Pi 3 Model B+
- Cảm biến cảm ứng (ví dụ: mô-đun cảm biến chạm điện dung)
- Màn hình LCD 16x2 I2C
- Microphone USB hoặc thiết bị đầu vào âm thanh tương thích khác 

## Yêu cầu phần mềm
- Hệ điều hành Raspbian (hoặc bất kỳ hệ điều hành Raspberry Pi tương thích nào khác) 
- Python 3.x 
- Các thư viện Python cần thiết (cài đặt bằng pip install -r requirements.txt):

RPi.GPIO 
adafruit-blinka 
adafruit-circuitpython-charlcd 
pyttsx3 
SpeechRecognition

## SETUP
1. Kết nối mô-đun cảm biến chạm điện dung vào các chân GPIO trên Raspberry Pi theo bảng sơ đồ mạch (Schematic). 
2. Kết nối màn hình LCD 16x2 I2C vào Raspberry Pi. 
3. Kết nối microphone USB hoặc thiết bị đầu vào âm thanh vào Raspberry Pi (có thể kiểm tra bằng tai nghe bluetooth).
4. Sao chép kho dữ liệu về Raspberry Pi:

        git clone https://github.com/serenaphuong/glovekeyboard.git

5. Cài đặt các thư viện Python cần thiết:

        pip install -r requirements.txt

6. Chạy tập lệnh sau, đảm bảo bạn đang ở trong thư mục của tệp bạn đã sao chép:

        python run.py

## Cách sử dụng

- Chạm vào các mô-đun cảm biến chạm điện dung  để nhập ký tự. Mỗi cảm biến sẽ được gán một nhóm chữ cái.
- Màn hình LCD hiển thị các ký tự ghép với nhau như một câu.
- Hệ thống chuyển đổi câu thành giọng nói và phát nó qua thiết bị âm thanh được kết nối.










