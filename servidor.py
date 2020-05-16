#!/usr/bin/python3
import json
import os
import socket
import threading
import sys
import time
from datetime import datetime
from getopt import getopt, GetoptError
from multiprocessing import Lock
from threading import Thread, BoundedSemaphore,Semaphore
from filtro import aplicar_filtro
from funciones_DB import guardar_ticket, listar_tickets
from funciones_generales import menu_edicion, procesamiento_csv, control_filtro, control_longitud_filtro
from modelo import MyEncoder, Ticket
from run_DB import session
from validaciones import logger, validar_numero
import math


def thread_fuction(port, sock, lista_clientes, lock,semaforo):
    while True:
        sys.stdout.flush()
        sys.stdin.flush()
        print(f"AL ENTRAR LA LISTA ES {lista_clientes}")
        # print(f"THREAD {threading.currentThread().getName()} {threading.currentThread().isAlive()}\n\n")
        # print(f"SOY LA PRIMERA LINEA DEL WHILE TRUE SERVIDOR! - THREAD {threading.currentThread().getName()}")
        msg = sock.recv(12)
        print(f"OPCION ES {msg.decode('ascii')} LONGITUD {len(msg.decode('ascii'))} THREAD {threading.currentThread().getName()}")
        print(f"Recibido  del puerto {port} atendido por PID {os.getpid()}:  {msg.decode('ascii')}")
        logger(sock, msg)  # logger para almacenar comandos realizados.
        if (msg.decode() == 'INSERTAR'):
            print(f"ENTRO A INSERTAR! THREAD {threading.currentThread().ident}")
            dict_data = sock.recv(1024).decode('ascii')
            print("PASO DICT_DATA")
            print(f"DICCIONARIO {dict_data}")
            final_data = json.loads(dict_data)
            print("PASO FINAL DATA")
            final_data = dict(final_data)
            print(f"entre con thread {threading.currentThread().ident}")
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
            with lock:
                guardar_ticket(autor, titulo, descripcion, estado, fecha=datetime.now())
            print("TICKET SE CREO!")
            sock.send("¡Ticket creado correctamente!\n".encode())
            #for cliente in lista_clientes:
                #if cliente is not sock:
                    #cliente.send("¡Se ha creado un nuevo ticket!".encode())
        elif (msg.decode() == 'LISTAR'):
            print(f"ENTRO A LISTAR! THREAD {threading.currentThread().ident}")
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
                print(f"PAGINA del THREAD {threading.currentThread().getName()}")
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

            if total_tickets>1:
                if lista_ids_edicion.count(identificador_ticket)>1:
                    while True:
                        if semaforo.acquire():
                            menu_edicion(sock, int(identificador_ticket))
                            lista_ids_edicion.remove(identificador_ticket)
                            semaforo.release()
                            break
                else:
                    menu_edicion(sock, int(identificador_ticket))
                    lista_ids_edicion.remove(identificador_ticket)
            else:
                semaforo.acquire()
                menu_edicion(sock, int(identificador_ticket))
                semaforo.release()
                lista_ids_edicion.remove(identificador_ticket)

        elif (msg.decode() == "LIMPIAR"):
            pass
        elif (msg.decode() == 'EXPORTAR'):
            test = json.loads(sock.recv(1024).decode('ascii'))  # Recivimos filtros o boolean lista completa.
            if control_filtro(test):
                continue
            print(f"VALOR TEST {test}")
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
            print("AL SALIR LISTA ES:\n")
            print(lista_clientes)
            break

        else:
            print('\nOpcion invalida!\n')


if __name__ == "__main__":
    # creamos el objeto socket
    try:
        (opt, arg) = getopt(sys.argv[1:], 'p:', ["puerto="])
        for opcion, valor in opt:
            if opcion in ("-p", "--puerto") and validar_numero(valor) is True:
                port = int(valor)
    except GetoptError as e:
        print("La estructura de comando es incorrecta.")
        sys.exit(1)

    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Fallo al crear el socket!')
        sys.exit(1)

    # Establecemos parametros
    host = '0.0.0.0'

    # Blindeamos el puerto y el host
    try:
        serversocket.bind((host, port))
    except NameError:
        print("Nunca se especifico el puerto!")
        sys.exit(1)
    # Establecemos 5 peticiones de escucha como maximo.
    serversocket.listen(5)
    lista_clientes = list()  # Lista que tiene los clientes actuales.
    lista_ids_edicion = list()
    lock = Lock()
    semaforo = Semaphore(1)
    i = 0
    while True:
        # Establecemos la conexion
        clientsocket, addr = serversocket.accept()
        if clientsocket:
            lista_clientes.append(clientsocket)
        print('Conexion establecida: SERVER ON')
        i += 1
        conection = Thread(name=f"Cliente {i}", target=thread_fuction,
                           args=(port, clientsocket, lista_clientes, lock,semaforo))
        conection.start()
