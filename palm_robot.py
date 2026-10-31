
import cv2
import mediapipe as mp
import serial
from serial.tools import list_ports
import time
from pathlib import Path

# =========================================
# SETTINGS - CHANGE ONLY IF NEEDED
# =========================================
# Set this to a port such as "COM13" to force a specific port.
# Leave it as None to detect an Arduino/USB serial device automatically.
ARDUINO_PORT ="COM13"
BAUD_RATE = 9600

# Use the successful index from camera_test.py
CAMERA_INDEX = 0
MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")

# =========================================
# CONNECT TO ARDUINO
# =========================================
arduino = None
camera = None
landmarker = None
last_command = None


def find_arduino_port():
    """Return the configured port or a detected Arduino/USB serial port."""
    ports = list(list_ports.comports())

    if ARDUINO_PORT:
       return ARDUINO_PORT

    keywords = (
        "arduino", "usb serial", "usb-serial", "ch340",
        "cp210", "ftdi", "silicon labs"
    )
    matches = [
        port.device for port in ports
        if any(keyword in port.description.lower() for keyword in keywords)
    ]

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        print("Multiple Arduino/USB serial ports found:", ", ".join(matches))
        print("Set ARDUINO_PORT near the top of palm_robot.py.")
        return None

    return None

def send_command(command):
    """Send F, B, L, R or S when the command changes."""
    global last_command

    if arduino is None or not arduino.is_open:
        return

    if command != last_command:
        arduino.write(command.encode("ascii"))
        arduino.flush()
        print(f"Gesture command: {command}")
        last_command = command


def main():
    global arduino, camera, landmarker

    if not MODEL_PATH.is_file():
        print(f"ERROR: Model file not found: {MODEL_PATH}")
        print("Put hand_landmarker.task beside palm_robot.py.")
        return

    # Connect to Arduino
    try:
        port = find_arduino_port()
        if port is None:
            print("ERROR: No Arduino/USB serial port was detected.")
            print("Connect the Arduino and check Windows Device Manager.")
            print("Then set ARDUINO_PORT to its COM number if automatic detection fails.")
            return

        print(f"Connecting to Arduino on {port}...")
        arduino = serial.Serial(
            port,
            BAUD_RATE,
            timeout=1,
            write_timeout=1
        )
        time.sleep(2)  # Arduino may reset when serial opens
        print("Arduino connected.")
    except (serial.SerialException, OSError) as error:
        print("ERROR: Cannot connect to Arduino:", error)
        print("Check the COM port and close Arduino Serial Monitor or other serial apps.")
        return

    try:
        # Open the laptop camera
        camera = cv2.VideoCapture(
            CAMERA_INDEX, cv2.CAP_DSHOW
        )

        if not camera.isOpened():
            print(f"ERROR: Cannot open camera {CAMERA_INDEX}.")
            print("Run camera_test.py and check the working index.")
            return

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Create MediaPipe hand detector
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        Options = mp.tasks.vision.HandLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode

        options = Options(
            base_options=BaseOptions(
                model_asset_path=str(MODEL_PATH)
            ),
            running_mode=RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        landmarker = HandLandmarker.create_from_options(options)

        start_time = time.monotonic()
        previous_timestamp = -1

        print("\nHand gesture robot started.")
        print("Top = Forward (F)")
        print("Bottom = Backward (B)")
        print("Left = Left (L)")
        print("Right = Right (R)")
        print("Center = Stop (S)")
        print("No hand / closed hand = Stop (S)")
        print("Press Q in the camera window to quit.")

        while True:
            success, frame = camera.read()

            if not success:
                print("ERROR: Cannot read camera frame.")
                send_command("S")
                break

            # Mirror the video so movement feels natural
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]

            # Draw center STOP zone
            left_edge = int(width * 0.35)
            right_edge = int(width * 0.65)
            top_edge = int(height * 0.35)
            bottom_edge = int(height * 0.65)

            cv2.rectangle(
                frame,
                (left_edge, top_edge),
                (right_edge, bottom_edge),
                (255, 255, 255),
                2
            )

            # Run hand landmark detection
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            timestamp_ms = int(
                (time.monotonic() - start_time) * 1000
            )
            timestamp_ms = max(
                timestamp_ms, previous_timestamp + 1
            )
            previous_timestamp = timestamp_ms

            result = landmarker.detect_for_video(
                mp_image, timestamp_ms
            )

            action = "NO HAND - STOP"
            command = "S"

            if result.hand_landmarks:
                points = result.hand_landmarks[0]

                # Finger extension check (index, middle,
                # ring and little finger)
                index_up = points[8].y < points[6].y
                middle_up = points[12].y < points[10].y
                ring_up = points[16].y < points[14].y
                little_up = points[20].y < points[18].y

                fingers_up = sum((
                    index_up, middle_up, ring_up, little_up
                ))

                # An open palm must have at least 3 fingers up
                if fingers_up >= 3:
                    palm_ids = (0, 5, 9, 13, 17)

                    palm_x = int(
                        sum(points[i].x for i in palm_ids)
                        / len(palm_ids) * width
                    )
                    palm_y = int(
                        sum(points[i].y for i in palm_ids)
                        / len(palm_ids) * height
                    )

                    cv2.circle(
                        frame, (palm_x, palm_y),
                        10, (0, 255, 255), -1
                    )

                    # Center has priority: STOP
                    if (
                        left_edge <= palm_x <= right_edge
                        and top_edge <= palm_y <= bottom_edge
                    ):
                        action, command = "STOP", "S"

                    # Outside the center: choose direction
                    elif palm_x < left_edge:
                        action, command = "LEFT", "L"

                    elif palm_x > right_edge:
                        action, command = "RIGHT", "R"

                    elif palm_y < top_edge:
                        action, command = "FORWARD", "F"

                    else:
                        action, command = "BACKWARD", "B"

                else:
                    action, command = "SHOW OPEN PALM", "S"

            # Stop if there is no hand or it is not open
            send_command(command)

            cv2.putText(
                frame, action, (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (0, 255, 0), 2
            )

            cv2.putText(
                frame, "FORWARD", (width // 2 - 60, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2
            )
            cv2.putText(
                frame, "BACKWARD",
                (width // 2 - 65, height - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2
            )
            cv2.putText(
                frame, "LEFT", (10, height // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2
            )
            cv2.putText(
                frame, "RIGHT", (width - 85, height // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2
            )
            cv2.putText(
                frame, "STOP",
                (width // 2 - 25, height // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2
            )

            cv2.imshow("Hand Gesture Robot", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nStopping robot...")

    except (serial.SerialException, OSError) as error:
        print("Hardware/serial error:", error)

    except Exception as error:
        print("Program error:", error)

    finally:
        # Send STOP before closing the serial connection
        if arduino is not None and arduino.is_open:
            try:
                arduino.write(b"S")
                arduino.flush()
                time.sleep(0.1)
            except (serial.SerialException, OSError):
                pass

        if landmarker is not None:
            landmarker.close()

        if camera is not None:
            camera.release()

        cv2.destroyAllWindows()

        if arduino is not None and arduino.is_open:
            arduino.close()

        print("Program closed. Stop command sent if connected.")


if __name__ == "__main__":
    main()
