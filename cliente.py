import getopt
import socket, sys
from funciones_generales import csv_manager, procesamiento_csv, validar_comando, parsear_comando
from modelo import Ticket
from run_DB import session
from filtro import filtrar_autor, filtrar_estado, filtrar_fecha, mostrar_menu_filtro
from funciones_DB import listar_tickets
from validaciones import validar_estado, validar_ticket, clear_screen
import json
from filtro import aplicar_filtro,mostrar_filtro
import errno
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket Creado!")
except socket.error:
    print ('Fallo al crear el socket!')
    sys.exit()

host = "localhost"
port = int(8070)

client_socket.connect((host, port))
print ('Socket conectado al host', host, 'en el puerto', port)
print("\t\t\tComandos Disponibles\n\t--insertar/-i\n\t--listar/-l\n\t--editar/-e nro_ticket\n\tUtilizar:\n\t\t\t-a nombre_autor\n\t\t\t-d estado\n\t\t\t-f fecha(DD-MM-YYYY)\n\tAgregandolo a listar (para filtrar) o a exportar\n\t--clear/-c\n\t--salir/-s\n")
while True:

    entrada = input('>>> ')

    opcion,test=validar_comando(entrada.lower())
    client_socket.sendto(opcion.encode(), (host, port))

    if (opcion == 'INSERTAR' and test is True):
        sys.stdin.flush() #debemos limpiar el buffer
        autor = input("\nIngrese autor del Ticket: ")
        titulo = input("\nIngrese titulo del ticket: ")
        descripcion = input("\nIngrese descripcion del ticket: ")
        estado = input("\nIngrese estado del ticket (pendiente, en procesamiento o resuelto): ")
        while validar_estado(estado):
            estado=input("Estado debe ser uno de los pedidos, intentelo nuevamente: ")
        data={"autor":autor,"titulo":titulo,"descripcion":descripcion,"estado":estado}
        json_data=json.dumps(data) #Convertimos el diccionario a JSON
        client_socket.sendto(json_data.encode(),(host,port))
        print(client_socket.recv(1024).decode()) #Mensaje de feedback satisfactorio.
    elif (opcion == 'LISTAR' and test is True):
        listar_tickets()
        mensaje_exito=client_socket.recv(1024).decode()
        print(mensaje_exito)

    elif (opcion == 'FILTRAR' and test is not None):
        lista_tickets=session.query(Ticket).filter()
        lista_tickets=aplicar_filtro(test,lista_tickets)
        mostrar_filtro(lista_tickets)
        mensaje_exito = client_socket.recv(1024).decode()
        print(mensaje_exito)

    elif (opcion == 'EDITAR' and test is not None):
        if test is False:
            continue
        client_socket.sendto(test.encode(), (host, port)) #Envio ID ticket al servidor
        menu=client_socket.recv(1024).decode()
        print(menu)
        edit_option=input("Opcion: ")
        while edit_option not in ('1','2','3'):
            edit_option = input("Opcion incorrecta, intentelo nuevamente: ")
        client_socket.sendto(edit_option.encode(), (host, port)) #Enviamos eleccion.

        nuevo_dato=input(client_socket.recv(4024).decode()) #Recivimos mensaje en funcion de la eleccion.
        if edit_option == '2':
            while validar_estado(nuevo_dato):
                nuevo_dato = input("El estado es incorrecto, intentelo nuevamente: ")
        client_socket.sendto(nuevo_dato.encode(), (host, port)) #Enviamos nuevo dato.
        mensaje_exito=client_socket.recv(1024).decode()
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
        mensaje_exito=client_socket.recv(1024).decode()
        print(mensaje_exito)
    elif (opcion == "SALIR"):
        break

    else:
        print('\nOpcion invalida!\n')
        input('Apretar Enter...')

client_socket.close()