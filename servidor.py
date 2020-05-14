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
from threading import Thread, BoundedSemaphore
from filtro import aplicar_filtro
from funciones_DB import guardar_ticket, listar_tickets
from funciones_generales import menu_edicion, procesamiento_csv, control_filtro, control_longitud_filtro
from modelo import MyEncoder, Ticket
from run_DB import session
from validaciones import logger, validar_numero
import math

def thread_fuction(port, sock, lista_clientes, i, lock, direccion):
    while True:
        print("SOY LA PRIMERA LINEA DEL WHILE TRUE SERVIDOR!")
        msg = None
        msg = clientsocket.recv(8)
        print(f"OPCION ES {msg.decode('ascii')} LONGITUD {len(msg.decode('ascii'))} THREAD {threading.currentThread().ident}")
        print(f"Recibido  del puerto {port} atendido por PID {os.getpid()}:  {msg.decode('ascii')}")
        logger(sock, msg)  # logger para almacenar comandos realizados.

        if (msg.decode() == 'INSERTAR'):
            with lock:
                #lock.acquire()
                print(f"ENTRO A INSERTAR! THREAD {threading.currentThread().ident}")
                dict_data=None
                #longitud_json=control_longitud_filtro(sock.recv(4).decode('ascii'))
                #print(f"LONGITUD ES {longitud_json}")
                #longitud_json=int(longitud_json)
                dict_data = sock.recv(1024).decode('ascii')
                control=["{\"","{"]
                for i in control:
                    if dict_data.count("{\"a") == 1:
                        break
                    if dict_data.count(i) == 0:
                        print(f"ENTRO AL IF! {dict_data}")
                        print(f"\n {i}")
                        dict_data = str(i) + dict_data
                        break
                """         if dict_data.count("{") == 0:
                    print(f"DENTRO DEL ELSE {dict_data}")
                    dict_data = "{" + dict_data
                elif dict_data.count("{\"") == 0:
                    print(f"DENTRO DEL IF {dict_data}")
                    dict_data = "{\""+dict_data"""

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
                guardar_ticket(autor, titulo, descripcion, estado, fecha=datetime.now())
                print("TICKET SE CREO!")
                sock.send("¡Ticket creado correctamente!\n".encode())
            #lock.release()
        elif (msg.decode() == 'LISTAR'):
            print(f"LA DIRECCION ES {socket.gethostbyname(socket.gethostname())}")
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
                    control = sock.recv(1024).decode()
                    lista_dict = dict()

        elif (msg.decode() == 'FILTRAR'):

            lista_tickets = session.query(Ticket).filter()
            filtros = sock.recv(1024).decode()
            filtros_dict = json.loads(filtros)
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
            block = None
            identificador_ticket = sock.recv(5).decode('ascii')  # Recibo ID del cliente.
            lista_ids_edicion.append(identificador_ticket)
            print(f"Lista actual: {lista_ids_edicion.count(identificador_ticket)}\n\n")
            total_tickets = len(lista_ids_edicion)
            menu_edicion(sock, int(identificador_ticket))

            """
                        if total_tickets>1:
                if lista_ids_edicion.count(identificador_ticket)>1:
                        print("hola")
                        while True:
                            print("while true")
                            if lock.acquire():
                                print("lock acquires")
                                menu_edicion(sock, host, port, int(identificador_ticket))
                                lista_ids_edicion.remove(identificador_ticket)
                                break
                else:
                    print("ELSE DE IF PEQUEÑO")
                    menu_edicion(sock, host, port, int(identificador_ticket))
                    lista_ids_edicion.remove(identificador_ticket)
            else:
                lock.acquire()
                menu_edicion(sock, host, port, int(identificador_ticket))
                lock.release()
                lista_ids_edicion.remove(identificador_ticket)
                print("ELSE >1")
                    # VER CONDITION VARIABLES de threading Condition
                    # https://docs.python.org/2.0/lib/condition-objects.html
                """

        elif (msg.decode() == "LIMPIAR"):
            pass
        elif (msg.decode() == 'EXPORTAR'):
            test = json.loads(sock.recv(1024).decode())  # Recivimos filtros o boolean lista completa.
            if control_filtro(test):
                continue
            print(f"VALOR TEST {test}")
            lista_tickets = session.query(Ticket).filter()
            if test is not True:
                lista_tickets = aplicar_filtro(test, lista_tickets)
            ticket_dict=dict()
            for ticket in lista_tickets:
                ticket_dict[ticket.ticketId] = ticket
            longitud_json=len(json.dumps(ticket_dict, cls=MyEncoder))
            print(f"LONGITUD ES {longitud_json}")
            sock.send(str(longitud_json).encode('ascii'))
            sock.send(json.dumps(ticket_dict, cls=MyEncoder).encode('ascii'))
            #sock.send("\n¡Tickets exportados con exito!\n".encode('ascii'))

        elif (msg.decode() == "SALIR"):
            for ip, puerto in lista_clientes:
                ip_actual, puerto_actual = sock.getpeername()
                if puerto_actual == puerto:
                    lista_clientes.remove((ip, puerto))

        else:
            print('\nOpcion invalida!\n')

        if not msg or msg in {"", " ", None}:
            break


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
    semaforo = BoundedSemaphore()
    while True:
        # Establecemos la conexion
        clientsocket, addr = serversocket.accept()
        lista_clientes.append(clientsocket.getpeername())
        print('Conexion establecida: SERVER ON')
        i = 0
        conection = Thread(target=thread_fuction, args=(port, clientsocket, lista_clientes, i, lock, addr))
        conection.start()
