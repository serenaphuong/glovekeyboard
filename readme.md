# Touch-and-Speak Raspberry Pi Project
# https://pimylifeup.com/raspberry-pi-anydesk/
## Overview

This project demonstrates a Raspberry Pi-based system that allows users to input text using touch sensors, convert the text to speech, and recognize speech to display it on an LCD screen.

## Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi 3 Model B+)
- Touch sensors (e.g., capacitive touch sensors)
- 16x2 I2C LCD screen
- USB microphone or other compatible audio input device

## Software Requirements

- Raspbian OS (or any other compatible Raspberry Pi operating system)
- Python 3.x
- Required Python libraries (install using `pip install -r requirements.txt`):
  - RPi.GPIO
  - adafruit-blinka
  - adafruit-circuitpython-charlcd
  - pyttsx3
  - SpeechRecognition

## Setup

1. Connect the touch sensors to the designated GPIO pins on the Raspberry Pi.
2. Connect the 16x2 I2C LCD screen to the Raspberry Pi.
3. Connect a USB microphone or audio input device to the Raspberry Pi.
4. Clone the repository to your Raspberry Pi:

    ```bash
    git clone https://github.com/smart-life-tech/serena.git
    ```

5. Install the required Python libraries:

    ```bash
    pip install -r requirements.txt
    ```

6. Run the main scripts one at a time, make sure you are in the diectory of the file you cloned:

    ```bash
    python lcdOnly.py
    python tts-stt.py
    python withoutSpeech.py
    python keypadTest.py
    python withspeech/speech.py
    ```

## Usage

1. Touch the sensors to input characters. Each sensor is assigned a pair of alphabets.
2. A double touch space or a timeout period signifies the end of a sentence.
3. The LCD screen displays the accumulated characters as a sentence.
4. The system converts the sentence to speech and plays it using the connected audio device.

## Customization
##note main.py could be any of the file from the repo above
- Adjust GPIO pin configurations in `main.py` if your touch sensors are connected to different pins.
- Modify the alphabet pairs in `main.py` based on your sensor mapping.
- Tweak the timeout duration and other settings in `main.py` to suit your preferences.

## License

This project is licensed under the [MIT License](LICENSE).

