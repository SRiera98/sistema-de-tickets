#!/usr/bin/python3
import os
import socket
import sys
import threading
from multiprocessing import Lock
from threading import Thread
from funciones_generales import control_ejecucion_servidor
from funciones_servidor import almacenar_ticket, solicitar_tickets, configurar_servidor, \
    exportar_tickets_servidor,editar_tickets_servidor
from validaciones import logger


def thread_fuction(port, sock, lock):
    while True:
        sys.stdout.flush()
        sys.stdin.flush()
        msg = sock.recv(12) # Recibimos la opción dada por el socket cliente.
        print(f"Recibido  del puerto {port} atendido por PID {os.getpid()} - Cliente {threading.currentThread().getName()}:  {msg.decode('ascii')}")

        logger(sock, msg)  # logger para almacenar comandos realizados.

        if (msg.decode() == 'INSERTAR'):
            almacenar_ticket(sock, lock)
        elif (msg.decode() == 'LISTAR'):
            solicitar_tickets(msg, sock)

        elif (msg.decode() == 'FILTRAR'):
            if solicitar_tickets(msg, sock) is False:
                continue

        elif (msg.decode() == 'EDITAR'):
            identificador_ticket = sock.recv(5).decode('ascii')  # Recibo ID del cliente.
            if identificador_ticket == 'False':
                continue
            editar_tickets_servidor(sock, int(identificador_ticket))

        elif (msg.decode() == "LIMPIAR"):
            pass

        elif (msg.decode() == 'EXPORTAR'):
            if exportar_tickets_servidor(sock) is False:
                continue

        elif (msg.decode() == "SALIR"):
            break

        else:
            print('\n¡Opcion inválida!\n')


if __name__ == "__main__":
    # Definimos el host y el puerto a utilizar.
    port=control_ejecucion_servidor()
    host = '0.0.0.0' # El socket atenderá en todas las Direcciones IP locales.

    # Llamamos al metodo que configura el servidor y devuelve el socket.
    serversocket=configurar_servidor(host,port)

    lock = Lock() # Lock para lograr que la creacion de tickets sea de uno a la vez.
    i = 0 # Solo para darle un nombre al thread.
    while True:
        # Establecemos la conexion
        clientsocket, addr = serversocket.accept()
        i += 1
        print(f'¡Conexion de Cliente {i} establecida!')
        conection = Thread(name=f"Cliente {i}", target=thread_fuction, args=(port, clientsocket, lock))
        conection.start()
