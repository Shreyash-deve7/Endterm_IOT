import socket
import threading

HOST = 'localhost'
PORT = 5000
BUFF_SIZE = 1024

clients = []
lock = threading.Lock()
names = {}

def send_to_all(msg, skip_sock=None):
    lock.acquire()
    try:
        for s in clients:
            if s != skip_sock:
                try:
                    s.send(msg.encode())
                except:
                    pass
    finally:
        lock.release()

def handle_client(sock, addr):
    client_name = "User_" + str(addr[1])
    
    try:
        data = sock.recv(BUFF_SIZE).decode()
        if data.startswith("NAME:"):
            client_name = data[5:].strip()
        
        lock.acquire()
        names[sock] = client_name
        lock.release()
        
        print(f"+ {client_name} connected from {addr}")
        
        msg = f"*** {client_name} joined ***\n"
        send_to_all(msg, sock)
        
        sock.send(f"Welcome {client_name}!\n".encode())
        
        while True:
            incoming = sock.recv(BUFF_SIZE).decode().strip()
            
            if not incoming:
                break
            
            print(f"[{client_name}]: {incoming}")
            send_to_all(f"[{client_name}]: {incoming}\n", sock)
    
    except:
        pass
    
    finally:
        lock.acquire()
        try:
            if sock in clients:
                clients.remove(sock)
            n = names.pop(sock)
        except:
            n = client_name
        lock.release()
        
        send_to_all(f"*** {n} left ***\n")
        print(f"- {n} disconnected")
        sock.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    
    print(f"Server started on {HOST}:{PORT}")
    
    try:
        while True:
            c, a = s.accept()
            
            lock.acquire()
            clients.append(c)
            lock.release()
            
            print(f"+ Connection from {a}")
            
            t = threading.Thread(target=handle_client, args=(c, a))
            t.start()
    
    except KeyboardInterrupt:
        print("\nClosing...")
    finally:
        s.close()

if __name__ == "__main__":
    main()
