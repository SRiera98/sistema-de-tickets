import math
import socket
import sys
import time
from datetime import datetime
import json
from filtro import aplicar_filtro
from funciones_DB import guardar_ticket
from funciones_generales import control_filtro, menu_edicion
from modelo import Ticket, MyEncoder
from run_DB import session


def almacenar_ticket(sock,lock):
    dict_data = sock.recv(1024).decode('ascii')
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
    with lock:
        guardar_ticket(autor, titulo, descripcion, estado, fecha=datetime.now())
    sock.send("¡Ticket creado correctamente!\n".encode())

def solicitar_tickets(msg,sock):
    lista_tickets = session.query(Ticket)
    if msg.decode() == 'FILTRAR':
        # Realizo los pasos de filtro previos
        lista_tickets = session.query(Ticket).filter()
        filtros = sock.recv(1024).decode('ascii')
        filtros_dict = json.loads(filtros)
        if control_filtro(filtros_dict):
            return False
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
            control = sock.recv(4).decode('ascii')
            lista_dict = dict()

def editar_ticket_servidor(sock,lista_ids_edicion,semaforo):
    identificador_ticket = sock.recv(5).decode('ascii')  # Recibo ID del cliente.
    lista_ids_edicion.append(identificador_ticket) #Añado a lista de IDs para ver si otros threads eligen editar un mismo ticket.
    total_tickets = len(lista_ids_edicion) #longitud actual de la lista de IDs de tickets.
    if total_tickets > 1:
        if lista_ids_edicion.count(identificador_ticket) > 1:
            control_aviso = True
            sock.send(str(control_aviso).encode())
            sock.send("¡Este ticket esta siendo editado!\nEsperando...".encode())
            while True:
                if semaforo.acquire():
                    menu_edicion(sock, int(identificador_ticket))
                    lista_ids_edicion.remove(identificador_ticket)
                    semaforo.release()
                    break
        else:
            control_aviso = False
            sock.send(str(control_aviso).encode())
            menu_edicion(sock, int(identificador_ticket))
            lista_ids_edicion.remove(identificador_ticket)
    else:
        semaforo.acquire()
        control_aviso = False
        sock.send(str(control_aviso).encode())
        menu_edicion(sock, int(identificador_ticket))
        semaforo.release()
        lista_ids_edicion.remove(identificador_ticket)

def exportar_tickets_servidor(sock):
    test = json.loads(sock.recv(1024).decode('ascii'))  # Recibimos filtros o boolean lista completa.
    if control_filtro(test):
        return False
    lista_tickets = session.query(Ticket)
    if test is not True:  # En caso de que sea un filtro.
        lista_tickets = session.query(Ticket).filter()
        lista_tickets = aplicar_filtro(test, lista_tickets)

    total_paginas = math.ceil(len(lista_tickets.all()) / 10)  # dividimos el total de tickets por la cantidad de paginas
    ticket_dict = dict()
    sock.send(str(total_paginas).encode('ascii'))
    num_pagina = -1
    while True:
        num_pagina += 1
        query = lista_tickets.limit(10).offset(num_pagina * 10)
        current_pages = session.execute(query).fetchall()
        for i in current_pages:
            ticket = Ticket(ticketId=i[0], fecha=i[1], titulo=i[2], autor=i[3], descripcion=i[4], estado=i[5])
            ticket_dict[ticket.ticketId] = ticket
        datos = json.dumps(ticket_dict, cls=MyEncoder)
        sock.send(datos.encode('ascii'))  # Enviamos  diccionario JSON
        ticket_dict = dict()
        time.sleep(0.04)  # Necesario debido a que sin el sleep, se producen errores en el envio de datos.
        if num_pagina == total_paginas:
            break
    if total_paginas>0:
        sock.send("¡Tickets exportados con exito!\n".encode())


def configurar_servidor(host,port):
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
    except TypeError:
        print("¡El puerto ingresado es invalido!")
        sys.exit(1)
    except OverflowError:
        print("El puerto ingresado es invalido, recuerde: ¡el puerto debe estar entre 0-65535!")
        sys.exit(1)
    # Establecemos un backlog de 5 peticiones de espera de conexion como maximo.
    serversocket.listen(5)
    return serversocket