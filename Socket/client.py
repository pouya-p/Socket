import socket
import sys
import time
import os



SERVER = sys.argv[1]
PORT = int(sys.argv[2])
BUFFER = 1000
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = 'Quit'
SEPARATOR = 'split'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def quit():
    client.send((DISCONNECT_MESSAGE).encode(FORMAT))
    print('[-] [Client] Server Connection Ended.')


def send_file(file_name, file_name_des):
    file_size = os.path.getsize(file_name)
    client.send(
        f'{file_name}{SEPARATOR}{file_size}{SEPARATOR}{file_name_des}'.encode(FORMAT))

    with open(file_name, 'rb') as reader:
        while True:
            bytes_read = reader.read(BUFFER)
            client.sendall(bytes_read)
            if not bytes_read:
                break

        print(
            f'File With Name ({file_name}) and With Size ({file_size}) sucessfuly Sended.')


def list_file():
    print('[+] [Client] Requesting Files...\n')
    client.send('1'.encode(FORMAT))
    number_of_Files = client.recv(BUFFER).decode(FORMAT)

    K = 0
    print('=======================    LIST OF FILES    =======================')
    client.send('2'.encode(FORMAT))
    for i in range(int(number_of_Files)):
        client.send('S'.encode(FORMAT))
        received = client.recv(BUFFER).decode(FORMAT)
        file_name, file_time, file_size = received.split(SEPARATOR)
        K += 1
        print(
            f'{K}- {file_name:30}{time.ctime(float(file_time)):30}{int(file_size)/1024} KB')
        client.send('E'.encode(FORMAT))

    client.send('3'.encode(FORMAT))
    total_dire_size = client.recv(BUFFER).decode(FORMAT)
    print(f'Total Files : {number_of_Files}')
    print(f'Total Directory Size : {int(total_dire_size)/1024} KB')


def download(file_name, file_name_des_dl):
    client.send(file_name.encode(FORMAT))

    file_size = client.recv(BUFFER).decode(FORMAT)
    file_size = float(file_size)

    if file_size == -1:
        print('File Not Found!. Enter the Name Correctly.')
        return 0

    bytes_recevi = 0
    print('[+] [Client] Downloading...')
    with open(file_name_des_dl, 'wb') as writer:
        while bytes_recevi < file_size:
            temp = client.recv(BUFFER)
            writer.write(temp)
            bytes_recevi += len(temp)

    print(f'File with Name {(file_name_des_dl)} Successfuly Downloaded.')


def delete(file_name_delete):
    print(f'Deleting file : {(file_name_delete)}')

    client.send(file_name_delete.encode(FORMAT))

    file_exists = client.recv(BUFFER).decode(FORMAT)
    if file_exists == '-1':
        print('[-] [Client] File dose not exists on server.')
        return 0

    confirmation_delete = input(
        f'Are you sure to delete file {file_name_delete} ? (Y/N)')
    while confirmation_delete != 'Y' and confirmation_delete != 'N' and confirmation_delete != 'y' and confirmation_delete != 'n':
        print('Enter valid Input .')
        confirmation_delete = input(
            f'Are you sure to delete file {(file_name_delete)} ? (Y/N)')

    if confirmation_delete == 'Y' or confirmation_delete == 'y':
        client.send('Y'.encode(FORMAT))

        confirmation_status = client.recv(BUFFER).decode(FORMAT)
        if confirmation_status == '1':
            print(
                f'[+] [Client] File with Name {file_name_delete} Successfuly Deleted.')
            return 0
        else:
            print('File Failed to Delete.')

    else:
        client.send('N'.encode(FORMAT))
        print('Delete Canceled by Client.')
        return 0


print('[+] [Client] Client Request to Server...')
try:
    client.connect((SERVER, PORT))
    print('[+] [Client] Connection Sucessful.')

    connected = True
    while connected:
        info = input('\n==================\tEnter Your Command Number\t==================\n  1. Send File\n  2. Download File\n  3. List File (LS)\n  4. Delete File\n  5. Quit\n')
        if info == '1':
            client.send('Send File'.encode(FORMAT))
            file_name_send = input('Enter the File Name :')
            file_name_des_send = input(
                'Select the File Name to be Stored on the Server: ')
            if file_name_send and file_name_des_send:
                send_file(file_name_send, file_name_des_send)
            else:
                print('Enter the Valid File Name.')

        elif info == '2':
            client.send('Download File'.encode(FORMAT))
            file_name_dl = input('Enter the File Name :')
            file_name_des_dl = input(
                'Enter the File Name to be Downloaded on the Client:')
            if file_name_dl and file_name_des_dl:
                download(file_name_dl, file_name_des_dl)
            else:
                print('Enter the file name corrcetly.')

        elif info == '3':
            client.send('List File'.encode(FORMAT))
            list_file()

        elif info == '4':
            client.send('Delete File'.encode(FORMAT))
            file_name_delete = input('enter the file name:')
            if file_name_delete:
                delete(file_name_delete)
            else:
                print('enter the valid file name.')

        elif info == '5':
            quit()
            connected = False

    client.close()


except:
    print('[-] [Client] Connection Unsucessful.')
