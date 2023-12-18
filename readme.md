## Tổng quan
Dự án này thể hiện một hệ thống dựa trên Raspberry Pi cho phép người dùng nhập văn bản bằng cảm biến cảm ứng, chuyển đổi văn bản thành giọng nói và nhận diện giọng nói để hiển thị nó trên một màn hình LCD.

## Yêu cầu phần cứng
Raspberry Pi (đã kiểm tra trên Raspberry Pi 3 Model B+)
Cảm biến cảm ứng (ví dụ: cảm biến cảm ứng điện dung)
Màn hình LCD 16x2 I2C
Microphone USB hoặc thiết bị đầu vào âm thanh tương thích khác
Yêu cầu phần mềm
Hệ điều hành Raspbian (hoặc bất kỳ hệ điều hành Raspberry Pi tương thích nào khác)
Python 3.x
Các thư viện Python cần thiết (cài đặt bằng pip install -r requirements.txt):
RPi.GPIO
adafruit-blinka
adafruit-circuitpython-charlcd
pyttsx3
SpeechRecognition
## Thiết lập
Kết nối cảm biến cảm ứng vào các chân GPIO được chỉ định trên Raspberry Pi.

Kết nối màn hình LCD 16x2 I2C vào Raspberry Pi.

Kết nối microphone USB hoặc thiết bị đầu vào âm thanh vào Raspberry Pi.

Sao chép kho dữ liệu về Raspberry Pi của bạn:

```bash
 git clone https://github.com/serenaphuong/glovekeyboard
    ```

Cài đặt các thư viện Python cần thiết:

```bash
   pip install -r requirements.txt
    ```



Chạy các tập lệnh chính một cách tuần tự, đảm bảo bạn đang ở trong thư mục của tệp bạn đã sao chép:

```bash
    python run.py
    ```


## Sử dụng
Chạm vào các cảm biến để nhập ký tự. Mỗi cảm biến được gán một cặp chữ cái.
Một lần chạm kép khoảng trắng hoặc một khoảng thời gian chờ sẽ đánh dấu kết thúc một câu.
Màn hình LCD hiển thị các ký tự tích lũy như một câu.
Hệ thống chuyển đổi câu thành giọng nói và phát nó qua thiết bị âm thanh được kết nối.
## Tùy chỉnh
Điều chỉnh cấu hình chân GPIO trong main.py nếu cảm biến cảm ứng của bạn được kết nối vào các chân khác.
Sửa đổi các cặp chữ cái trong main.py dựa trên ánh xạ cảm biến của bạn.
Điều chỉnh thời gian chờ và các thiết lập khác trong main.py để phù hợp với sở thích của bạn.
## Giấy phép
Dự án này được cấp phép theo Giấy phép MIT.






