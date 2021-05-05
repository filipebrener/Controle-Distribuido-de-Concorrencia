import socket
import os
import time
import threading
# bind_ip = ip do servidor
bind_ip = '192.168.0.112'
bind_port = 12000

lock = threading.Lock()
                        #Códigos de cada operação {REQUEST,RELEASE,GRANT}
REQUEST = '1'     
RELEASE = '2'
GRANT = '3'

requests_socket = []      #fila em ordem FIFO onde contem os sockets dos requests
requests_pid = []         #fila em ordem FIFO onde contem os PIDs do request
clients = {}              #tabela: key= PID_do_client value= N° de request atendido 

def recv_connection():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip,bind_port))
    server.listen()
    while True:
        client, addr = server.accept()
        client_handle = threading.Thread(target=process_handler,args=(client,))
        client_handle.start()

def process_handler(client_socket):
    while True:
        txt = client_socket.recv(8).decode()
        msg = txt.split('|')
        lock.acquire()
        if(msg[0] == REQUEST):                            #REQUEST  
            if(len(requests_socket) == 0):                #se não houver ninguém na fila
                send_grant(client_socket)
            requests_socket.append(client_socket)
            requests_pid.append(msg[1])
        elif(msg[0] == RELEASE):                          #RELEASE
            att_grant_number(msg[1])
            requests_socket.remove(requests_socket[0])
            requests_pid.remove(msg[1])
            if(len(requests_socket) > 0):                 #se houver alguém na fila
                send_grant(requests_socket[0])
        lock.release()

def send_grant(client_socket):
    grant_msg = GRANT + '|'
    grant_msg = bits_padding(grant_msg,8,'0')
    client_socket.send(grant_msg.encode())

def bits_padding(string,tam,charactere):
    dif = tam - len(string)
    for i in range(dif):
        string = string + charactere
    return string

def att_grant_number(pid):
    client = clients.get(pid)
    if client:
        clients[pid] += 1
    else:
        clients[pid] = 1

def interface():
    while True:
        os.system('cls')
        print('Digite uma das opções abaixo.')
        print('1 - Fila de pedidos atual')
        print('2 - Quantas vezes cada processo foi antendido')
        print('3 - Sair')
        user_choice = input('Opção: ')
        if(user_choice == '1'):
            show_current_queue()
        elif(user_choice == '2'):
            show_requests_pid()
        elif(user_choice == '3'):
            print('Até mais!')
            break
        else:
            print('\nOpção inválida!')
        input('\nPrescione qualquer tecla para continuar...')

def show_current_queue():
    os.system('cls')
    print('Fila de pedidos atual: \n') 
    i = 0
    lock.acquire()
    for pid in requests_pid:
        i += 1
        string = bits_padding((str(i) + ' '),6,' ')
        string += ('- ' + str(pid)) 
        print(string)
    lock.release()

def show_requests_pid():
    os.system('cls')
    print('Numero de requests atendidos de cada processo: \n') 
    lock.acquire()
    for pid in clients: 
        print(str(pid) + ' - ' + str(clients[pid]))
    lock.release()

if __name__ == '__main__':
    recv_connections = threading.Thread(target=recv_connection)
    recv_connections.start()
    interface()
