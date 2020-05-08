import json
import socket
import sys

from funciones_generales import validar_comando, control_ejecucion, control_longitud_filtro
from validaciones import validar_estado, clear_screen

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
        "\t\t\tComandos Disponibles\n\t--insertar/-i\n\t--listar/-l\n\t--editar/-e nro_ticket\n\t--exportar/-x\n\tUtilizar:\n\t\t\t-a nombre_autor\n\t\t\t-d estado\n\t\t\t-f fecha(DD-MM-YYYY)\n\tAgregandolo a listar (para filtrar) o a exportar\n\t--clear/-c\n\t--salir/-s\n")
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
            total_paginas=int(client_socket.recv(1024).decode())
            control="-s"
            num_pagina=-1
            while control=="-s":
                num_pagina+=1
                tickets=client_socket.recv(2000).decode()
                dict_tickets = json.loads(tickets)
                for k, v in dict_tickets.items():
                    for key, value in v.items():
                        print(f"{key}: {value}\t")
                    print("\n")
                if num_pagina==total_paginas:
                    break
                control=input("¿Desea ver más paginas? -s/-n: ")
                client_socket.sendto(control.encode(),(host,port))


        elif (opcion == 'FILTRAR' and test is not None):

            client_socket.sendto(json.dumps(test).encode(), (host, port))

            longitud = client_socket.recv(5).decode()
            longitud_int = control_longitud_filtro(longitud)

            dict_filtro = client_socket.recv(int(longitud_int))
            tickets = json.loads(dict_filtro.decode())

            if len(tickets) == 0:
                print("No hay resultados para la busqueda!\n")
            else:
                print(len(tickets))
                print("Resultados de la busqueda: \n")
                for k, v in tickets.items():
                    for key, value in v.items():
                        print(f"{key}: {value}\t")
                    print("\n")

            mensaje_exito = client_socket.recv(1024).decode()
            print(mensaje_exito)

        elif (opcion == 'EDITAR' and test is not None):
            if test is False:
                continue
            client_socket.sendto(test.encode(), (host, port))  # Envio ID ticket al servidor
            menu = client_socket.recv(1024).decode()  # Recibo el Menu desde el metodo menu_edicion
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
            client_socket.sendto(json.dumps(test).encode(),
                                 (host, port))  # Mandamos datos de filtro o  Boolean lista compelta
            mensaje_exito = client_socket.recv(1024).decode()
            print(mensaje_exito)
        elif (opcion == "SALIR" and test is True):
            client_socket.close()
            break

        else:
            print('\nOpcion invalida!\n')
            input('Apretar Enter...')
