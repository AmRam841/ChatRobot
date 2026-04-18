import socket
import threading
import select
import sys

# Server configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 12345      # Port for the chat server (different from SSH port)
BUFFER_SIZE = 1024

# Lists to keep track of connected clients
clients = []
client_addresses = {}
lock = threading.Lock()

def broadcast(message, sender_socket=None):
    """Sends a message to all connected clients, except the sender."""
    with lock:
        for client_socket in clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode('utf-8'))
                except:
                    # If sending fails, assume the client is disconnected
                    remove_client(client_socket)

def remove_client(client_socket):
    """Removes a client from the list and closes the connection."""
    if client_socket in clients:
        clients.remove(client_socket)
        addr = client_addresses.get(client_socket, 'Unknown')
        print(f"Client {addr} disconnected.")
        broadcast(f"System: Client {addr} has left the chat.\n")
        try:
            client_socket.close()
        except:
            pass # Socket might already be closed
        if client_socket in client_addresses:
            del client_addresses[client_socket]


def handle_client(client_socket, addr):
    """Handles a single client connection."""
    print(f"New connection from {addr}")
    with lock:
        clients.append(client_socket)
        client_addresses[client_socket] = addr

    broadcast(f"System: New user {addr} has joined the chat.\n", client_socket)
    client_socket.send("Welcome to the chatroom! Type your messages.\n".encode('utf-8'))

    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            if message:
                print(f"Received from {addr}: {message.strip()}")
                broadcast(f"[{addr}]: {message}", client_socket)
            else:
                # Empty message means client disconnected
                remove_client(client_socket)
                break
        except ConnectionResetError:
            remove_client(client_socket)
            break
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            remove_client(client_socket)
            break

def start_chat_server():
    """Starts the main chat server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(False) # Non-blocking socket

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Chat server listening on {HOST}:{PORT}")
    except socket.error as e:
        print(f"Could not bind to {HOST}:{PORT}. Error: {e}")
        sys.exit(1)

    # List of sockets to monitor (server socket + all client sockets)
    sockets_list = [server_socket]

    while True:
        try:
            # Use select to wait for activity on any socket
            readable, _, exceptional = select.select(sockets_list, [], sockets_list)

            for sock in readable:
                if sock == server_socket:
                    # New connection
                    client_socket, addr = server_socket.accept()
                    client_socket.setblocking(True) # Make client socket blocking for easier handling
                    # Start a new thread for each client
                    client_thread = threading.Thread(target=handle_client, args=(client_socket, str(addr[0]) + ":" + str(addr[1])))
                    client_thread.daemon = True # Allow program to exit even if threads are running
                    client_thread.start()
                else:
                    # Data from an existing client
                    # This part is now handled by the handle_client thread,
                    # but select can detect if a client socket is ready for reading.
                    # The thread will call recv. If recv fails, the thread handles removal.
                    pass # Threading handles this.

            # Handle exceptional conditions (e.g., client disconnects abruptly)
            for sock in exceptional:
                remove_client(sock)
                if sock in sockets_list:
                    sockets_list.remove(sock)

        except KeyboardInterrupt:
            print("Shutting down chat server...")
            break
        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
            # Attempt to clean up sockets
            for sock in sockets_list:
                try:
                    sock.close()
                except:
                    pass
            break

    server_socket.close()
    print("Chat server stopped.")

if __name__ == "__main__":
    start_chat_server()
