import socket
import sys
import time
from funciones_generales import control_filtro, procesamiento_csv
from modelo import Ticket
from validaciones import validar_estado
import json

def ingresar_ticket(client_socket):
    """
    Toma los datos para crear un nuevo ticket, enviando un json al servidor.
    :param client_socket: socket que representa el cliente.
    :return: Nada
    """
    sys.stdin.flush()  # debemos limpiar el buffer
    autor = input("\nIngrese autor del Ticket: ")
    titulo = input("\nIngrese titulo del ticket: ")
    descripcion = input("\nIngrese descripcion del ticket: ")
    estado = input("\nIngrese estado del ticket (pendiente, en procesamiento o resuelto): ")
    while validar_estado(estado):
        estado = input("Estado debe ser uno de los pedidos, intentelo nuevamente: ")
    data = {"autor": autor, "titulo": titulo, "descripcion": descripcion, "estado": estado}
    json_data = json.dumps(data)  # Convertimos el diccionario a JSON
    client_socket.send(json_data.encode())
    print(client_socket.recv(36).decode())  # Mensaje de feedback satisfactorio.


def consultar_tickets(client_socket,opcion,test):
    """
    Metodo que abarca tanto el filtrado como la lista completa de tickets.
    :param client_socket: socket que representa el cliente.
    :param opcion: La cual fue elegida por el cliente.
    :param test: Puede ser True en caso de la lista completa, o un diccionario
                 que contiene los filtros a aplicar.
    :return: Nada
    """
    if opcion == 'FILTRAR':
        time.sleep(0.02)
        client_socket.send(json.dumps(test).encode('ascii'))
        if control_filtro(test):
            return False
    total_paginas = int(client_socket.recv(1024).decode('ascii'))
    control = "-s"
    num_pagina = -1
    while control == "-s":
        num_pagina += 1
        tickets = client_socket.recv(2000).decode('ascii')
        dict_tickets = json.loads(tickets)
        if len(dict_tickets) == 0 and total_paginas == 0:
            print("¡No hay resultados para esa búsqueda/consulta!")
            break
        for k, v in dict_tickets.items():
            for key, value in v.items():
                print(f"{key}: {value}\t")
            print("\n")
        if num_pagina == total_paginas:
            break
        control = input("¿Desea ver más paginas? -s/-n: ")
        while control not in ("-s", '-n'):
            control = input("Opción incorrecto, recuerde: -s/-n: ")
        client_socket.send(control.encode('ascii'))

def editar_ticket_cliente(test,client_socket):
    """
    Toma los parametros del ticket a editar y los envia al servidor.
    :param test: ID del ticket a editar o False
    :param client_socket: socket que representa el cliente.
    :return: Nada
    """
    time.sleep(0.05)
    client_socket.send(str(test).encode('ascii'))  # Envio ID ticket al servidor
    if test is False:
        return False
    menu = client_socket.recv(1024).decode()  # Recibo el Menu desde el metodo menu_edicion
    print(menu)
    edit_option = input("Opcion: ")
    while edit_option not in ('1', '2', '3'):
        edit_option = input("Opcion incorrecta, intentelo nuevamente: ")
    client_socket.send(edit_option.encode('ascii'))  # Enviamos eleccion.

    nuevo_dato = input(client_socket.recv(64).decode('ascii'))  # Recibimos mensaje en funcion de la eleccion.
    if edit_option == '2':
        while validar_estado(nuevo_dato):
            nuevo_dato = input("El estado es incorrecto, intentelo nuevamente: ")
    client_socket.send(nuevo_dato.encode())  # Enviamos nuevo dato.
    mensaje_exito = client_socket.recv(1024).decode()
    print(mensaje_exito)

def exportar_tickets_cliente(client_socket,test):
    """
    Se encarga de recibir y exportar los tickets mediante un proceso.
    :param client_socket: socket que representa el cliente.
    :param test: Diccionario con filtro o True.
    :return: Nada
    """
    time.sleep(0.05)
    client_socket.send(json.dumps(test).encode('ascii'))  # Mandamos datos de filtro o  Boolean lista compelta
    if control_filtro(test):
        return False
    total_paginas = int(client_socket.recv(5).decode('ascii'))
    num_pagina = -1
    lista_tickets = list()
    while True:
        num_pagina += 1
        datos = client_socket.recv(2000).decode('ascii')
        tickets = json.loads(datos)
        if len(tickets) == 0 and total_paginas == 0:
            print("¡No hay resultados para esa búsqueda!")
            break
        for k, v in tickets.items():
            lista_tickets.append(Ticket(ticketId=v["ticketId"], fecha=v["fecha"], titulo=v["titulo"], autor=v["autor"],
                                        descripcion=v["descripcion"], estado=v["estado"]))
        if num_pagina == total_paginas:
            break
    if len(lista_tickets) > 0:
        procesamiento_csv(lista_tickets)
        mensaje_exito = client_socket.recv(36).decode()
        print(mensaje_exito)

def configurar_cliente(host,port):
    """
    Configura y devuelve un socket destinado a ser cliente.
    :param host: IP o alias al cual el socket se conectará
    :param port: Puerto al cual el socket se conectará
    :return: Objeto socket configurado.
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Fallo al crear el socket!')
        sys.exit(1)

    try:
        client_socket.connect((host, port))
    except NameError:
        print("¡Nunca se especifico el puerto o host!")
        sys.exit(1)
    except TypeError:
        print("¡La IP ingresada es invalida!")
        sys.exit(1)
    except OverflowError:
        print("El puerto ingresado es invalido, recuerde: ¡el puerto debe estar entre 0-65535!")
        sys.exit(1)
    except ConnectionRefusedError:
        print("¡Fallo en la conexion!, revise su configuracion e intente nuevamente.")
        sys.exit(1)
    return client_socket