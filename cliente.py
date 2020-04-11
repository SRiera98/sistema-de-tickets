import socket, sys

from funciones_generales import csv_manager, procesamiento_csv
from modelo import Ticket
from run_DB import session
from filtro import filtrar_autor, filtrar_estado, filtrar_fecha, mostrar_menu_filtro
from funciones_DB import listar_tickets
from validaciones import validar_estado
import json
from filtro import aplicar_filtro,mostrar_filtro
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket Creado!")
except socket.error:
    print ('Fallo al crear el socket!')
    sys.exit()

host = "localhost"
port = int(8080)

client_socket.connect((host, port))
print ('Socket conectado al host', host, 'en el puerto', port)

while True:
    print("""\n
        \t\t\t *** Menu ***
        - INSERTAR TICKET (INSERTAR)
        - LISTAR TICKETS (LISTAR)
        - EDITAR TICKETS (EDITAR)
        - FILTRAR TICKETS (FILTRAR)
        - EXPORTAR LISTA DE TICKETS (EXPORTAR)
        - SALIR (SALIR)
        """)

    opcion = input('Opcion: ').upper()

    client_socket.sendto(opcion.encode(), (host, port))
    if (opcion == 'INSERTAR'):
        autor = input("\nIngrese autor del Ticket: ")
        titulo = input("\nIngrese titulo del ticket: ")
        descripcion = input("\nIngrese descripcion del ticket: ")
        estado = input("\nIngrese estado del ticket (pendiente, en procesamiento o resuelto): ")
        while validar_estado(estado):
            estado=input("Estado debe ser uno de los pedidos, intentelo nuevamente): ")
        data={"autor":autor,"titulo":titulo,"descripcion":descripcion,"estado":estado}
        json_data=json.dumps(data) #Convertimos el diccionario a JSON
        client_socket.sendto(json_data.encode(),(host,port))

    elif (opcion == 'LISTAR'):
        listar_tickets()

    elif (opcion == 'FILTRAR'):

        lista_tickets=session.query(Ticket).filter()
        filtros=mostrar_menu_filtro()
        lista_tickets=aplicar_filtro(filtros,lista_tickets)
        mostrar_filtro(lista_tickets)

    elif (opcion == 'EDITAR'):
        listar_tickets()
        titulo_ticket = input("\nIngrese el indentificador del Ticket a editar: ")
        client_socket.sendto(titulo_ticket.encode(), (host, port))
        # print(client_socket.recv(1024).decode()) VER como hacer que imprima solo si esta mal.
        print(client_socket.recv(1024).decode())
        edit_option=input("Opcion: ")
        while edit_option not in ('1','2','3'):
            edit_option = input("Opcion incorrecta, intentelo nuevamente: ")
        client_socket.sendto(edit_option.encode(), (host, port))

        nuevo_dato=input(client_socket.recv(1024).decode())
        if edit_option == '2':
            while validar_estado(nuevo_dato):
                nuevo_dato = input("El estado es incorrecto, intentelo nuevamente: ")
        client_socket.sendto(nuevo_dato.encode(), (host, port))
    elif (opcion == "EXPORTAR"):
        lista_tickets = session.query(Ticket).filter()
        eleccion=input("¿Desea exportar una lista completa o una filtrada? (completa/filtrada): ").lower()
        while eleccion not in ("completa","filtrada"):
            eleccion = input("Su eleccion es incorrecta, recuerde elegir entre: (completa/filtrada) ")
        if eleccion == "completa":
            procesamiento_csv(lista_tickets)
        else:
            filtros = mostrar_menu_filtro()
            lista_tickets = aplicar_filtro(filtros, lista_tickets)
            procesamiento_csv(lista_tickets)

    elif (opcion == 'SALIR'):
        break

    else:
        print('\nOpcion invalida!\n')
        input('Apretar Enter...')

client_socket.close()