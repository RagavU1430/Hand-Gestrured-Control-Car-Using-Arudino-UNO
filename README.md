<div align="center">

# 🤖 Hand-Gesture Controlled Robot Car

### Drive a robot car naturally — with the position of your open palm.

Control an Arduino-powered robot car using real-time hand tracking from a laptop
camera. Move your hand around the video frame to steer, and place your palm in
the center zone to stop safely.

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-FF6F00?style=for-the-badge&logo=google&logoColor=white)
![Arduino](https://img.shields.io/badge/Arduino-UNO-00979D?style=for-the-badge&logo=arduino&logoColor=white)

</div>

---

## ✨ Features

- **Real-time hand tracking** with MediaPipe Hand Landmarker
- **Intuitive directional control** based on palm position
- **Safety-first stopping** when no hand, a closed hand, or the center zone is detected
- **Automatic Arduino serial-port discovery** with an optional fixed COM port
- **Command de-duplication** so repeated serial commands are not unnecessarily sent
- **Camera diagnostic tool** for finding a working camera index
- **Graceful shutdown** that sends a final stop command before disconnecting

## 🎮 Gesture Controls

Show an **open palm** with at least three fingers extended:

| Palm position in camera view | Action | Arduino command |
|---|---|:---:|
| Above the center zone | Move forward | `F` |
| Below the center zone | Move backward | `B` |
| Left of the center zone | Turn left | `L` |
| Right of the center zone | Turn right | `R` |
| Inside the center zone | Stop | `S` |
| No hand, closed hand, or invalid gesture | Stop | `S` |

> **Safety note:** Test with the wheels lifted off the ground first. Keep the
> emergency power switch accessible and stop the program with `Q` when needed.

## 🧩 How It Works

```text
Laptop camera
     │
     ▼
MediaPipe hand landmarks
     │
     ▼
Open-palm + palm-position classification
     │
     ▼
Serial command: F / B / L / R / S
     │
     ▼
Arduino UNO → motor driver → robot motors
```

The Python controller mirrors the camera image, divides it into directional
regions, and sends a new command only when the action changes. The Arduino
receives one-character commands at **9600 baud**.

## 🛠️ Requirements

### Hardware

- Arduino UNO
- 2-wheel or 4-wheel robot chassis
- Compatible motor driver and DC motors
- USB cable for the Arduino
- Laptop or desktop with a webcam
- Separate motor power supply appropriate for your motors

### Software

- Windows, macOS, or Linux
- Python 3.10 or newer
- Arduino IDE

Python packages:

```text
opencv-python
mediapipe
pyserial
```

## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/RagavU1430/Hand-Gestrured-Control-Car-Using-Arudino-UNO.git
   cd Hand-Gestrured-Control-Car-Using-Arudino-UNO
   ```

2. **Create and activate a virtual environment** *(recommended)*

   Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   macOS/Linux:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   python -m pip install --upgrade pip
   python -m pip install opencv-python mediapipe pyserial
   ```

## ⚙️ Configuration

Open [`palm_robot.py`](palm_robot.py) and review these settings:

```python
ARDUINO_PORT = "COM13"  # Set to None for automatic detection
BAUD_RATE = 9600
CAMERA_INDEX = 0
```

- Set `ARDUINO_PORT` to your Arduino’s port, such as `COM5`, or use `None`
  to enable automatic detection.
- Change `CAMERA_INDEX` if your webcam is not camera index `0`.
- Keep the baud rate synchronized with the Arduino sketch.

## ▶️ Running the Project

### 1. Find a working camera

```bash
python camera_test.py
```

The tool checks camera indexes `0` through `4`. Press **Q** to close the test
window.

### 2. Upload the Arduino motor-control sketch

Open `motor_control.ino` in the Arduino IDE, add the motor-driver pin mapping
and command handling for `F`, `B`, `L`, `R`, and `S`, then upload it to the
Arduino UNO.

> `motor_control.ino` is currently a placeholder. The exact wiring and pin
> assignments depend on the motor driver and chassis being used.

### 3. Start hand control

With the Arduino connected and the robot safely supported:

```bash
python palm_robot.py
```

Press **Q** in the camera window to exit. The controller sends `S` before
closing when the serial connection is still available.

## 🧯 Troubleshooting

| Problem | What to check |
|---|---|
| Arduino is not detected | Confirm the USB cable, close Arduino Serial Monitor, and set `ARDUINO_PORT` manually |
| Camera will not open | Run `camera_test.py`, check camera permissions, and update `CAMERA_INDEX` |
| Model file not found | Keep `hand_landmarker.task` in the same folder as `palm_robot.py` |
| Robot moves in the wrong direction | Swap motor polarity or adjust direction logic in the Arduino sketch |
| Commands are received but motors do not move | Check motor-driver wiring, motor power, common ground, and the `S` stop logic |
| Tracking is unstable | Improve lighting, keep the palm visible, and move farther from the camera |

## 📁 Project Structure

```text
Hand_Gesture_Robot/
├── camera_test.py        # Finds and previews available cameras
├── hand_landmarker.task  # MediaPipe hand-tracking model
├── motor_control.ino     # Arduino motor-control sketch placeholder
├── palm_robot.py         # Hand tracking and serial command controller
├── .gitignore
├── LICENSE
└── README.md
```

## 🔮 Possible Improvements

- Add a complete motor-driver implementation for a selected driver board
- Add gesture-based speed control
- Add smoothing or a short command hold time to reduce jitter
- Add an on-screen serial connection and battery-status indicator
- Add support for multiple hands or custom gestures

## 📄 License

This project is distributed under the [MIT License](LICENSE).

<div align="center">

### Built with curiosity, computer vision, and a little engineering magic. ✋⚡

</div>
