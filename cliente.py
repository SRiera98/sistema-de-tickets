#!/usr/bin/python3
import socket
import sys
from funciones_cliente import ingresar_ticket, consultar_tickets, configurar_cliente, editar_ticket_cliente, \
    exportar_tickets_cliente
from funciones_generales import validar_comando, controlar_ejecucion_cliente
from validaciones import clear_screen

if __name__ == "__main__":
    # Obtenemos host y puerto de lo pasado en GetOpt
    host, port = controlar_ejecucion_cliente()

    # Llamamos al metodo que crea y conecta el socket con el servidor y devuelve dicho socket.
    client_socket = configurar_cliente(host,port)

    print(f"Socket conectado al host {host}, en el puerto {port}")
    print("\t\t\tComandos Disponibles\n\t--insertar/-i\n\t--listar/-l\n\t--editar/-e nro_ticket\n\t--exportar/-x\n\tUtilizar:\n\t\t\t-a nombre_autor\n\t\t\t-d estado\n\t\t\t-f fecha (DD-MM-YYYY)\n\tAgregandolo a listar (para filtrar) o a exportar\n\t--clear/-c\n\t--salir/-s\n")
    while True:
        sys.stdout.flush()
        sys.stdin.flush()
        #control_creacion_ticket(client_socket)
        entrada = input('>>> ')

        opcion, test = validar_comando(entrada.lower())

        client_socket.send(opcion.encode('ascii'))

        if (opcion == 'INSERTAR' and test is True):
            ingresar_ticket(client_socket)

        elif (opcion == 'LISTAR' and test is True):
            consultar_tickets(client_socket, opcion, test)

        elif (opcion == 'FILTRAR' and test is not None):
            if consultar_tickets(client_socket, opcion, test) is False:
                continue

        elif (opcion == 'EDITAR' and test is not None):
            if editar_ticket_cliente(test, client_socket) is False:
                continue

        elif (opcion == 'LIMPIAR' and test is True):
            clear_screen()

        elif (opcion == "EXPORTAR" and (test is True or test is not None)):
            if exportar_tickets_cliente(client_socket,test) is False:
                continue

        elif (opcion == "SALIR" and test is True):
            client_socket.close()
            break

        else:
            print('\nOpcion invalida!\n')
            input('Apretar Enter...')
