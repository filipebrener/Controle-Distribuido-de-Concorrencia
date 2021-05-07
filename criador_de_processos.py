import socket
import os
from datetime import datetime
import threading
import time

#bind_ip = ip do servidor
bind_ip = '192.168.0.112'
bind_port = 12000

REQUEST = '1'
RELEASE = '2'
GRANT = '3'
lock = threading.Lock()
r = 1000             # número de vezes que os processos vão repetir 
n = 128              # número de processos
k = 0                # tempo em segundos que o processo vai esperar antes de dar o release
num_exec = r*n 
current_exec = [0]

def init_file():
    file = open('resultado.txt','w+')
    file.write('PID    | TIME\n')
    file.close()

def write_in_file():
    pid = str(threading.get_ident())
    dif = 6 - len(pid)
    for i in range(0,dif):
        pid = pid + " "
    current_time = datetime.now().strftime('%H:%M:%S.%f')
    file = open('resultado.txt','a+')
    file.write(pid + ' | ' + current_time + '\n')
    time.sleep(k)
    file.close()
    current_exec[0] += 1

def bits_padding(word,tam,charactere):
    dif = tam - len(word)
    for i in range(dif):
        word = word + charactere
    return word

def connect_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((bind_ip,bind_port))
    return server_socket

def send_request(server_socket):
    request_msg = REQUEST + '|' + str(threading.get_ident()) + '|' 
    request_msg = bits_padding(request_msg,8,'0')
    server_socket.send(request_msg.encode())

def recv_grant(server_socket):
    msg = server_socket.recv(8).decode()
    msg = msg.split('|')
    if(msg[0] == GRANT):
        write_in_file()

def send_release(server_socket):
    release_msg = RELEASE + '|' + str(threading.get_ident()) + '|' 
    release_msg = bits_padding(release_msg,8,'0')
    server_socket.send(release_msg.encode())

def exe_process():
    server_socket = connect_server()
    for i in range(r):
        send_request(server_socket)
        recv_grant(server_socket)
        send_release(server_socket)
    server_socket.close()

def handle_time(time):
    time = time.split('|')
    time = time[1].split(' ')
    time = time[1]
    time = datetime.strptime(time,'%H:%M:%S.%f ')
    return time

def calculate_time():
    file = open('resultado.txt', 'r')
    linhas = file.readlines()
    file.close()
    first_time = linhas[1]
    last_time = linhas[len(linhas)-1]
    first_time = handle_time(first_time)
    last_time = handle_time(last_time)
    dif = last_time - first_time    
    file = open('resultado.txt', 'a')
    file.write('\n###########################\n')
    file.write('Execution time: ' + str(dif) + '\n')
    file.write('r: ' + str(r) + '\n')
    file.write('n: ' + str(n) + '\n')
    file.write('k: ' + str(k) + '\n')
    file.close()

if __name__ == '__main__':
    os.system('cls')
    init_file()
    processos = []
    for i in range(n):
        processo = threading.Thread(target=exe_process)
        processos.append(processo)
    
    for processo in processos:
        processo.start()

    while (current_exec[0] != num_exec):
        os.system('cls')
        current_percent = round((current_exec[0]/num_exec)*100,2)
        print('Execução em: ' + str(current_percent) + '%')
        time.sleep(1)
    os.system('cls')
    print('Execução Completa!')
    calculate_time()
