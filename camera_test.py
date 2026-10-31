
import cv2

def main():
    for index in range(5):
        print(f"Trying camera index {index}...")

        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

        if not cap.isOpened():
            print(f"Camera {index} could not be opened.")
            cap.release()
            continue

        # Allow the camera a moment to initialize
        success, frame = False, None

        for _ in range(10):
            success, frame = cap.read()
            if success:
                break
            cv2.waitKey(100)

        if success:
            print(f"Camera works! Index = {index}")
            print("Press Q in the camera window to close.")

            while True:
                success, frame = cap.read()

                if not success:
                    print("Camera stopped providing frames.")
                    break

                cv2.imshow("Camera Test", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            cap.release()
            cv2.destroyAllWindows()
            return

        print(f"Camera {index} opened but returned no image.")
        cap.release()

    cv2.destroyAllWindows()
    print("No working camera found.")
    print("Check Windows camera permissions and close other camera apps.")

if __name__ == "__main__":
    main()
