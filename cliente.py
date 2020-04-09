import socket, sys
from modelo import Ticket
from run_DB import session
from filtro import filtrar_autor, filtrar_estado, filtrar_fecha
from validaciones import validar_estado
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

while True:
    print("""\n
        \t\t\t *** Menu ***
        - INSERTAR TICKET (INSERTAR)
        - LISTAR TICKETS (LISTAR)
        - EDITAR TICKETS (EDITAR)
        - FILTRAR TICKETS (FILTRAR)
        - SALIR (SALIR)
        """)

    opcion = input('Opcion: ').upper()

    client_socket.sendto(opcion.encode(), (host, port))
    if (opcion == 'INSERTAR'):
        autor = input("\nIngrese autor del Ticket: ")
        client_socket.sendto(autor.encode(), (host, port))
        titulo = input("\nIngrese titulo del ticket: ")
        client_socket.sendto(titulo.encode(), (host, port))
        descripcion = input("\nIngrese descripcion del ticket: ")
        client_socket.sendto(descripcion.encode(), (host, port))
        estado = input("\nIngrese estado del ticket (pendiente, en procesamiento o resuelto): ")
        while validar_estado(estado):
            estado=input("Estado debe ser uno de los pedidos, intentelo nuevamente): ")
        client_socket.sendto(estado.encode(), (host, port))

    elif (opcion == 'LISTAR'):
        lista_tickets=session.query(Ticket).filter().all()
        print("Los Tickets actuales sin resolver son: ")
        for ticket in lista_tickets:
            print(f"Titulo: {ticket.titulo}\nAutor: {ticket.autor}\nFecha de Creacion: {ticket.fecha}\nDescripcion: {ticket.descripcion}\nEstado: {ticket.estado}\n\n")

    elif (opcion == 'FILTRAR'):
        exit=False
        entry=0
        lista_tickets=session.query(Ticket).filter()
        filtros = list()
        test="yes"
        while not exit and entry<3:
            filtro=input("Ingrese el tipo de filtro por el que desea comenzar (fecha, autor o estado):").lower()
            while filtro not in ("fecha","autor","estado"):
                filtro=input("Filtro incorrecto, intentelo nuevamente: ")
            filtros.append(filtro)
            if entry<2 and test == "yes":
                test=input("¿Desea añadir otro filtro? (yes/no): ")
                entry += 1
                exit=False
                if test == "no":
                    exit=True
            else:
                exit=True

        for filtro in filtros:
            if filtro == "autor":
                lista_tickets=filtrar_autor(lista_tickets)
            if filtro == "estado":
                lista_tickets=filtrar_estado(lista_tickets)
            if filtro == "fecha":
                lista_tickets=filtrar_fecha(lista_tickets)
        if lista_tickets.count()==0:
            print("No hay resultados para su busqueda!\n")
        else:
            print("Resultados de la busqueda: \n")
            for ticket in lista_tickets:
                print(f"Titulo: {ticket.titulo}\nAutor: {ticket.autor}\nFecha de Creacion: {ticket.fecha}\nDescripcion: {ticket.descripcion}\nEstado: {ticket.estado}\n\n")

    elif (opcion == 'EDITAR'):
        titulo_ticket = input("\nIngrese el titulo del Ticket a editar: ")
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
    elif (opcion == 'SALIR'):
        break

    else:
        print('\nOpcion invalida!\n')
        input('Apretar Enter...')

client_socket.close()