#!/usr/bin/python3
from multiprocessing import Lock, RLock
import sys, socket, os
from threading import Thread, BoundedSemaphore
import threading
from funciones_generales import menu_edicion
from run_DB import session
from modelo import Ticket
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
import json
from validaciones import logger
from funciones_DB import guardar_ticket
import time


def thread_fuction(port, sock, lista_clientes, i, semaforo):
    while True:
        msg = clientsocket.recv(1024)
        print(f"Recibido  del puerto {port} atendido por PID {os.getpid()}:  {msg.decode()}")
        logger(sock, msg) #logger para almacenar comandos realizados.

        if (msg.decode() == 'INSERTAR'):
            with lock:

                dict_data = sock.recv(1024).decode()
                final_data = json.loads(dict_data)
                final_data = dict(final_data)

                for key, value in final_data.items():
                    if key == "autor":
                        autor = value
                    elif key == "titulo":
                        titulo = value
                    elif key == "descripcion":
                        descripcion = value
                    elif key == "estado":
                        estado = value
                print(final_data)
                guardar_ticket(autor, titulo, descripcion, estado, fecha=datetime.now())
                sock.sendto("¡Ticket creado correctamente!\n".encode(),(host,port))
            # for ip,puerto in lista_clientes:
            # ip_actual,puerto_actual=sock.getpeername()
            # if not puerto_actual==puerto:
            # sock.sendto(f"El cliente de Puerto {puerto_actual} agrego un ticket!".encode(), (host, puerto))
        elif (msg.decode() == 'LISTAR'):
            sock.sendto("\n¡Comando OK!\n".encode(),(host,port))

        elif (msg.decode() == 'EDITAR'):
            block = None
            identificador_ticket = sock.recv(4024).decode() #Recibo ID del cliente.
            lista_ids_edicion.append(identificador_ticket)
            print(f"Lista actual: {lista_ids_edicion.count(identificador_ticket)}\n\n")
            menu_edicion(sock, host, port, identificador_ticket)
            """
            for i in range(len(lista_ids_edicion)):
                for j in range(len(lista_ids_edicion)-1):
                    if len(lista_ids_edicion)==1 or lista_ids_edicion[i] == lista_ids_edicion[j+1]:
                        lock.acquire() #Revisar
                        menu_edicion(sock, host, port, identificador_ticket)
                        lock.release()
                    else:
                        menu_edicion(sock,host,port,identificador_ticket)
            
            
            if len(lista_ids_edicion) == 1:
                semaforo.acquire()
                menu_edicion(sock, host, port, identificador_ticket)
                semaforo.release()
                lista_ids_edicion.remove(identificador_ticket)
            elif len(lista_ids_edicion) > 1:
                if identificador_ticket in lista_ids_edicion:
                    block = True
                elif identificador_ticket not in lista_ids_edicion:
                    block = False
                if block:
                    lista_ids_edicion.remove(identificador_ticket)
                    # VER CONDITION VARIABLES de threading Condition
                    # https://docs.python.org/2.0/lib/condition-objects.html
                """
        elif (msg.decode() == 'FILTRAR'):
            sock.sendto("\n¡Comando OK!\n".encode(), (host, port))
        elif (msg.decode() == "LIMPIAR"):
            pass
        elif (msg.decode() == 'EXPORTAR'):
            sock.sendto("\n¡Tickets exportados con exito!\n".encode(), (host, port))
            pass
        elif (msg.decode() == 'SALIR'):
            for ip, puerto in lista_clientes:
                ip_actual, puerto_actual = sock.getpeername()
                if puerto_actual == puerto:
                    lista_clientes.remove((ip, puerto))

        else:
            print('\nOpcion invalida!\n')

        if not msg or msg in {"", " ", None}:
            break


# creamos el objeto socket
try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Fallo al crear el socket!')
    sys.exit()

# Establecemos parametros
host = "localhost"
port = int(8070)

# Blindeamos el puerto y el host
serversocket.bind((host, port))

# Establecemos 5 peticiones de escucha como maximo.
serversocket.listen(5)
if __name__ == "__main__":
    lista_clientes = list()  # Lista que tiene los clientes actuales.
    lista_ids_edicion = list()
    lock = Lock()
    semaforo = BoundedSemaphore()
    while True:
        # Establecemos la conexion
        clientsocket, addr = serversocket.accept()
        lista_clientes.append(clientsocket.getpeername())
        print('Conexion establecida: SERVER ON')
        i = 0
        conection = Thread(target=thread_fuction, args=(port, clientsocket, lista_clientes, i, semaforo))
        conection.start()
