import socket
import threading
import sys
import os


SERVER = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])
BUFFER = 100000
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = 'Quit'
SEPARATOR = 'split'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))


def handle_client(client_conn, addr):

    def receive_file():
        recevied = client_conn.recv(BUFFER).decode(FORMAT)
        file_name, file_size, file_name_des = recevied.split(SEPARATOR)
        file_name = os.path.basename(file_name)
        file_size = int(file_size)

        with open(file_name_des, 'wb') as f:
            len_bytes_recevie = 0
            while len_bytes_recevie < file_size:
                bytes_recevie = client_conn.recv(BUFFER)
                f.write(bytes_recevie)
                len_bytes_recevie += len(bytes_recevie)

        print(
            f'File With Name ({file_name}) and With Size ({file_size}) Sucessfuly Recevied.')

    def list_file():
        ack = client_conn.recv(BUFFER).decode(FORMAT)
        if ack == '1':
            print('[+] [SERVER] Listing Files...')

            listing = os.listdir(os.getcwd())
            client_conn.send(str(len(listing)).encode(FORMAT))
            total_dirc_size = 0

        ack = client_conn.recv(BUFFER).decode(FORMAT)
        if ack == '2':
            for file in listing:
                temp = client_conn.recv(BUFFER).decode(FORMAT)
                if temp == 'S':
                    client_conn.send(
                        f'{file}{SEPARATOR}{str(os.path.getctime(file))}{SEPARATOR}{str(os.path.getsize(file))}'.encode(FORMAT))
                    total_dirc_size += os.path.getsize(file)
                temp = client_conn.recv(BUFFER).decode(FORMAT)

        ack = client_conn.recv(BUFFER).decode(FORMAT)
        if ack == '3':

            total_dirc_size = str(total_dirc_size)
            client_conn.send((total_dirc_size).encode(FORMAT))
            print('[+] [SERVER] Successfully Sent File Listing.')

    def download():
        file_name = client_conn.recv(BUFFER).decode(FORMAT)

        if os.path.isfile(file_name):
            client_conn.send(str(os.path.getsize(file_name)).encode(FORMAT))

        else:
            print(f'File with Name {file_name} Not Valid.')
            client_conn.send('-1'.encode(FORMAT))
            return 0

        print('[+] [SERVER] Sending File...')
        with open(file_name, 'rb') as reader:
            while True:
                bytes_send = reader.read(BUFFER)
                client_conn.sendall(bytes_send)
                if not bytes_send:
                    break

        print(f'[+] [SERVER] File with Name {(file_name)} Sucessfuly Sended.')

    def delete():
        file_name = client_conn.recv(BUFFER).decode(FORMAT)

        if os.path.isfile(file_name):
            client_conn.send('1'.encode(FORMAT))
        else:
            client_conn.send('-1'.encode(FORMAT))
            return 0

        confirmation_delete = client_conn.recv(BUFFER).decode(FORMAT)

        if confirmation_delete == 'Y':
            os.remove(file_name)
            client_conn.send('1'.encode(FORMAT))

        else:
            print('[-] [SERVER] Delete Canceled By Client.')
            return 0

        print(
            f'[+] [SERVER] File With Name {(file_name)} Successfuly Deleted on Server.')

    print(f"[+] [NEW CONNCETION] {addr} connected.")

    connected = True
    while connected:
        msg = client_conn.recv(BUFFER).decode(FORMAT)
        if msg:
            print(f'[+] [SERVER] Message Client {addr} is : {msg}')
            if msg == DISCONNECT_MESSAGE:
                connected = False

            elif msg == 'Send File':
                receive_file()

            elif msg == 'Download File':
                download()

            elif msg == 'List File':
                list_file()

            elif msg == 'Delete File':
                delete()

    client_conn.close()
    print(f'[+] [SERVER] Active Connenctions : {threading.activeCount() - 2}')


print('[+] [SERVER] server is starting...')
server.listen()
print(f'[+] [SERVER] server is listening on {SERVER} , {PORT}')
while True:
    client_conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(client_conn, addr))
    thread.start()
    print(f"[+] [SERVER] Active Connections : {threading.activeCount() - 1}")
