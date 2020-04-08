#!/usr/bin/python3
import sys, socket, os
from threading import Thread
from run_DB import session
from modelo import Ticket
from datetime import datetime

def thread_fuction(port,sock):
    while True:
        msg = clientsocket.recv(1024)
        print(f"Recibido  del puerto {port} atendido por PID {os.getpid()}:  {msg.decode()}")

        if (msg.decode() == 'INSERTAR'):
            autor = sock.recv(1024).decode()
            titulo = sock.recv(1024).decode()
            descripcion=sock.recv(1024).decode()
            estado=sock.recv(1024).decode()
            print(f"autor {autor} titulo {titulo} descripcion {descripcion} estado {estado}")
            ticket=Ticket(autor=autor,titulo=titulo,descripcion=descripcion,estado=estado,fecha=datetime.now())
            session.add(ticket)
            session.commit()
            break
        elif (msg.decode() == 'LISTAR'):
            pass

        elif (msg.decode() == 'FILTRAR'):
            pass

        elif (msg.decode() == 'SALIR'):
            break

        else:
            print('\nOpcion invalida!\n')

        if not msg or msg in {""," ",None}:
            break


# creamos el objeto socket
try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Fallo al crear el socket!')
    sys.exit()

#Establecemos parametros
host = "localhost"
port = int(8080)

# Blindeamos el puerto y el host
serversocket.bind((host, port))

# Establecemos 5 peticiones de escucha como maximo.
serversocket.listen(5)

while True:
    # establish a connection
    clientsocket, addr = serversocket.accept()
    print('Conexion establecida: SERVER ON')
    conection=Thread(target=thread_fuction,args=(port,clientsocket))
    conection.start()

