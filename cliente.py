import json
import socket
import sys
import time

import jsonpickle

from filtro import aplicar_filtro, mostrar_filtro
from funciones_DB import listar_tickets
from funciones_generales import procesamiento_csv, validar_comando, control_ejecucion
from modelo import Ticket
from run_DB import session
from validaciones import validar_estado, clear_screen, validar_numero
import pickle
if __name__ == "__main__":

    host, port = control_ejecucion()

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Fallo al crear el socket!')
        sys.exit(1)

    try:
        client_socket.connect((host, port))
    except NameError:
        print("Nunca se especifico el puerto o host!")
        sys.exit(1)
    except ConnectionRefusedError:
        print("¡Fallo en la conexion!, revise su configuracion e intente nuevamente.")
        sys.exit(1)

    print('Socket conectado al host', host, 'en el puerto', port)
    print(
        "\t\t\tComandos Disponibles\n\t--insertar/-i\n\t--listar/-l\n\t--editar/-e nro_ticket\n\tUtilizar:\n\t\t\t-a nombre_autor\n\t\t\t-d estado\n\t\t\t-f fecha(DD-MM-YYYY)\n\tAgregandolo a listar (para filtrar) o a exportar\n\t--clear/-c\n\t--salir/-s\n")
    while True:

        entrada = input('>>> ')

        opcion, test = validar_comando(entrada.lower())
        client_socket.sendto(opcion.encode(), (host, port))

        if (opcion == 'INSERTAR' and test is True):
            sys.stdin.flush()  # debemos limpiar el buffer
            autor = input("\nIngrese autor del Ticket: ")
            titulo = input("\nIngrese titulo del ticket: ")
            descripcion = input("\nIngrese descripcion del ticket: ")
            estado = input("\nIngrese estado del ticket (pendiente, en procesamiento o resuelto): ")
            while validar_estado(estado):
                estado = input("Estado debe ser uno de los pedidos, intentelo nuevamente: ")
            data = {"autor": autor, "titulo": titulo, "descripcion": descripcion, "estado": estado}
            json_data = json.dumps(data)  # Convertimos el diccionario a JSON
            client_socket.sendto(json_data.encode(), (host, port))
            print(client_socket.recv(1024).decode())  # Mensaje de feedback satisfactorio.
        elif (opcion == 'LISTAR' and test is True):
            longitud=client_socket.recv(1024).decode()
            tickets=client_socket.recv(int(longitud))
            dict_tickets=json.loads(tickets.decode())
            for k,v in dict_tickets.items():
                for key,value in v.items():
                    print(f"{key}: {value}\t")
                print("\n")
            mensaje_exito = client_socket.recv(1024).decode()
            print(mensaje_exito)

        elif (opcion == 'FILTRAR' and test is not None):
            lista_tickets = session.query(Ticket).filter()
            lista_tickets = aplicar_filtro(test, lista_tickets)
            mostrar_filtro(lista_tickets)
            mensaje_exito = client_socket.recv(1024).decode()
            print(mensaje_exito)

        elif (opcion == 'EDITAR' and test is not None):
            if test is False:
                continue
            client_socket.sendto(test.encode(), (host, port))  # Envio ID ticket al servidor
            menu = client_socket.recv(1024).decode()
            print(menu)
            edit_option = input("Opcion: ")
            while edit_option not in ('1', '2', '3'):
                edit_option = input("Opcion incorrecta, intentelo nuevamente: ")
            client_socket.sendto(edit_option.encode(), (host, port))  # Enviamos eleccion.

            nuevo_dato = input(client_socket.recv(4024).decode())  # Recibimos mensaje en funcion de la eleccion.
            if edit_option == '2':
                while validar_estado(nuevo_dato):
                    nuevo_dato = input("El estado es incorrecto, intentelo nuevamente: ")
            client_socket.sendto(nuevo_dato.encode(), (host, port))  # Enviamos nuevo dato.
            mensaje_exito = client_socket.recv(1024).decode()
            print(mensaje_exito)

        elif (opcion == 'LIMPIAR' and test is True):
            clear_screen()

        elif (opcion == "EXPORTAR" and (test is True or test is not None)):
            lista_tickets = session.query(Ticket).filter()
            if test is True:
                procesamiento_csv(lista_tickets)
            else:
                lista_tickets = aplicar_filtro(test, lista_tickets)
                procesamiento_csv(lista_tickets)
            mensaje_exito = client_socket.recv(1024).decode()
            print(mensaje_exito)
        elif (opcion == "SALIR" and test is True):
            client_socket.close()
            break

        else:
            print('\nOpcion invalida!\n')
            input('Apretar Enter...')
