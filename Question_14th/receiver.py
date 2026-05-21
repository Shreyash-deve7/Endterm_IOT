import cv2
import numpy as np
import socket

def main():
    bind_address = ("127.0.0.1", 5005)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(bind_address)

    print("Waiting for frames on 127.0.0.1:5005. Press 'q' to quit.")

    while True:
        data, addr = sock.recvfrom(65536)

        frame_array = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        if frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)

        cv2.imshow("Received Stream - Edges", edges)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    sock.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
