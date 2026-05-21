import socket
import threading
import time

HOST = 'localhost'
PORT = 5000
BUFF = 1024

running = True

def receive_msgs(s):
    global running
    try:
        while running:
            msg = s.recv(BUFF).decode()
            if not msg:
                print("\nServer closed")
                running = False
                break
            print(f"\n{msg}", end='')
            print(">> ", end='', flush=True)
    except:
        running = False

def send_msgs(s, name):
    global running
    try:
        while running:
            text = input(">> ").strip()
            if not text:
                continue
            if text == "/quit":
                print("Exiting...")
                running = False
                break
            try:
                s.send(text.encode())
            except:
                running = False
                break
    except KeyboardInterrupt:
        running = False
    except:
        running = False

def main():
    global running
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Trying to connect {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print("Connected!\n")
        
        name = input("Your name: ").strip()
        if not name:
            name = "Guest"
        
        s.send(f"NAME:{name}".encode())
        
        welcome = s.recv(BUFF).decode()
        print(welcome)
        
        recv = threading.Thread(target=receive_msgs, args=(s,))
        recv.start()
        
        send = threading.Thread(target=send_msgs, args=(s, name))
        send.start()
        
        recv.join()
        send.join()
    
    except ConnectionRefusedError:
        print(f"Cannot connect to server at {HOST}:{PORT}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            s.close()
        except:
            pass
        running = False

if __name__ == "__main__":
    main()
