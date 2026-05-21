import cv2
import socket

def main():
    server_address = ("127.0.0.1", 5005)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open the webcam.")
        return

    print("Streaming frames to 127.0.0.1:5005. Press Ctrl+C to stop.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab a frame.")
                break

            frame = cv2.resize(frame, (640, 480))
            result, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if not result:
                continue

            sock.sendto(buffer.tobytes(), server_address)
    except KeyboardInterrupt:
        print("Stopped streaming.")
    finally:
        cap.release()
        sock.close()

if __name__ == "__main__":
    main()
