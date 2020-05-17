#!/usr/bin/python3
import json
import math
import os
import socket
import sys
import threading
import time
from datetime import datetime
from getopt import getopt, GetoptError
from multiprocessing import Lock
from threading import Thread, Semaphore
from filtro import aplicar_filtro
from funciones_DB import guardar_ticket, listar_tickets
from funciones_generales import menu_edicion, control_filtro
from funciones_servidor import almacenar_ticket
from modelo import MyEncoder, Ticket
from run_DB import session
from validaciones import logger, validar_numero


def thread_fuction(port, sock, lista_clientes, lock,semaforo):
    while True:
        sys.stdout.flush()
        sys.stdin.flush()
        msg = sock.recv(12) # Recibimos la opción dada por el socket cliente.
        print(f"OPCION ES {msg.decode('ascii')} LONGITUD {len(msg.decode('ascii'))} THREAD {threading.currentThread().getName()}")
        print(f"Recibido  del puerto {port} atendido por PID {os.getpid()}:  {msg.decode('ascii')}")
        logger(sock, msg)  # logger para almacenar comandos realizados.
        if (msg.decode() == 'INSERTAR'):
            almacenar_ticket(sock, lock)
        elif (msg.decode() == 'LISTAR'):
            lista = listar_tickets()
            lista_dict = dict()
            total_paginas = math.ceil(len(lista) / 10)  # dividimos el total de tickets por la cantidad de paginas
            sock.send(str(total_paginas).encode('ascii'))
            control = "-s"
            num_pagina = -1
            while control == "-s":
                num_pagina += 1
                query = session.query(Ticket).limit(10).offset(num_pagina * 10)
                current_pages = session.execute(query).fetchall()
                for i in current_pages:
                    ticket = Ticket(ticketId=i[0], fecha=i[1], titulo=i[2], autor=i[3], descripcion=i[4], estado=i[5])
                    lista_dict[ticket.ticketId] = ticket
                datos = json.dumps(lista_dict, cls=MyEncoder)
                sock.send(datos.encode('ascii'))  # Enviamos  diccionario JSON
                if num_pagina == total_paginas:
                    break
                else:
                    control = sock.recv(4).decode('ascii')
                    lista_dict = dict()

        elif (msg.decode() == 'FILTRAR'):

            lista_tickets = session.query(Ticket).filter()
            filtros = sock.recv(1024).decode()
            filtros_dict = json.loads(filtros)
            if control_filtro(filtros_dict):
                continue
            lista_tickets = aplicar_filtro(filtros_dict, lista_tickets)
            lista_dict = dict()
            total_paginas = math.ceil(
                len(lista_tickets.all()) / 10)  # dividimos el total de tickets por la cantidad de paginas
            sock.send(str(total_paginas).encode('ascii'))
            control = "-s"
            num_pagina = -1
            while control == "-s":
                num_pagina += 1
                query = lista_tickets.limit(10).offset(num_pagina * 10)
                current_pages = session.execute(query).fetchall()
                for i in current_pages:
                    ticket = Ticket(ticketId=i[0], fecha=i[1], titulo=i[2], autor=i[3], descripcion=i[4], estado=i[5])
                    lista_dict[ticket.ticketId] = ticket
                datos = json.dumps(lista_dict, cls=MyEncoder)
                sock.send(datos.encode('ascii'))  # Enviamos  diccionario JSON
                if num_pagina == total_paginas:
                    break
                else:
                    control = sock.recv(1024).decode()
                    lista_dict = dict()

        elif (msg.decode() == 'EDITAR'):
            identificador_ticket = sock.recv(5).decode('ascii')  # Recibo ID del cliente.
            lista_ids_edicion.append(identificador_ticket)
            total_tickets=len(lista_ids_edicion)
            control_aviso=False
            if total_tickets>1:
                if lista_ids_edicion.count(identificador_ticket)>1:
                    control_aviso=True
                    sock.send(str(control_aviso).encode('ascii'))
                    sock.send("¡Este ticket esta siendo editado!\nEsperando...".encode())
                    while True:
                        if semaforo.acquire():
                            menu_edicion(sock, int(identificador_ticket))
                            lista_ids_edicion.remove(identificador_ticket)
                            semaforo.release()
                            break
                else:
                    control_aviso = False
                    sock.send(str(control_aviso).encode('ascii'))
                    menu_edicion(sock, int(identificador_ticket))
                    lista_ids_edicion.remove(identificador_ticket)
            else:
                semaforo.acquire()
                control_aviso=False
                sock.send(str(control_aviso).encode('ascii'))
                menu_edicion(sock, int(identificador_ticket))
                semaforo.release()
                lista_ids_edicion.remove(identificador_ticket)

        elif (msg.decode() == "LIMPIAR"):
            pass
        elif (msg.decode() == 'EXPORTAR'):
            test = json.loads(sock.recv(1024).decode('ascii'))  # Recivimos filtros o boolean lista completa.
            if control_filtro(test):
                continue
            if test is True:
                lista_tickets = listar_tickets()
                total_paginas = math.ceil(len(lista_tickets) / 10)  # dividimos el total de tickets por la cantidad de paginas
            else:
                lista_tickets = session.query(Ticket).filter()
                lista_tickets = aplicar_filtro(test, lista_tickets)
                total_paginas = math.ceil(len(lista_tickets.all()) / 10)  # dividimos el total de tickets por la cantidad de paginas
            ticket_dict = dict()
            sock.send(str(total_paginas).encode('ascii'))
            num_pagina = -1
            while True:
                num_pagina += 1
                if test is True:
                    query = session.query(Ticket).limit(10).offset(num_pagina * 10)
                else:
                    query = lista_tickets.limit(10).offset(num_pagina * 10)
                current_pages = session.execute(query).fetchall()
                for i in current_pages:
                    ticket = Ticket(ticketId=i[0], fecha=i[1], titulo=i[2], autor=i[3], descripcion=i[4], estado=i[5])
                    ticket_dict[ticket.ticketId] = ticket
                datos = json.dumps(ticket_dict, cls=MyEncoder)
                sock.send(datos.encode('ascii'))  # Enviamos  diccionario JSON
                ticket_dict = dict()
                time.sleep(0.02)
                if num_pagina == total_paginas:
                    break
            sock.send("¡Tickets exportados con exito!\n".encode())

        elif (msg.decode() == "SALIR"):
            for cliente in lista_clientes:
                if cliente == sock:
                    lista_clientes.remove(cliente)
            break

        else:
            print('\n¡Opcion inválida!\n')


if __name__ == "__main__":
    # Establecemos host y puerto.
    try:
        (opt, arg) = getopt(sys.argv[1:], 'p:', ["puerto="])
        for opcion, valor in opt:
            if opcion in ("-p", "--puerto") and validar_numero(valor) is True:
                port = int(valor)
    except GetoptError as e:
        print("La estructura de comando es incorrecta.")
        sys.exit(1)

    host = '0.0.0.0'

    # creamos el objeto socket
    try:

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Fallo al crear el socket!')
        sys.exit(1)

    # Blindeamos el puerto y el host
    try:
        serversocket.bind((host, port))
    except NameError:
        print("Nunca se especifico el puerto!")
        sys.exit(1)
    except OverflowError:
        print("El puerto ingresado es invalido, recuerde: ¡el puerto debe estar entre 0-65535!")
        sys.exit(1)

    # Establecemos un backlog de 5 peticiones de espera de conexion como maximo.
    serversocket.listen(5)
    lista_clientes = list()  # Lista que tiene los clientes actuales.
    lista_ids_edicion = list() # lista que contiene los IDs para controlar la edicion de tickets
    lock = Lock() # Lock para lograr que la creacion de tickets sea de uno a la vez.
    semaforo = Semaphore(1) # Semaforo para lograr exclusion mutua en editar tickets iguales.
    i = 0
    while True:
        # Establecemos la conexion
        clientsocket, addr = serversocket.accept()
        if clientsocket:
            lista_clientes.append(clientsocket)
        print(f'¡Conexion de Cliente {i} establecida!')
        i += 1
        conection = Thread(name=f"Cliente {i}", target=thread_fuction,
                           args=(port, clientsocket, lista_clientes, lock,semaforo))
        conection.start()
