import socket, sys
from modelo import Ticket
from run_DB import session
from filtro import filtrar_autor, filtrar_estado, filtrar_fecha

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
        - SALIR (SALIR)
        - EDITAR TICKETS (EDITAR) -NO IMPLEMENTADO
        - FILTRAR TICKETS (FILTRAR) -NO IMPLEMENTADO
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

        while estado not in ("pendiente", "en procesamiento", "resuelto"):
            estado=input("Estado debe ser uno de los pedidos, intentelo nuevamente): ")
        client_socket.sendto(estado.encode(), (host, port))

    elif (opcion == 'LISTAR'):
        lista_tickets=session.query(Ticket).filter()
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

    elif (opcion == 'SALIR'):
        break

    else:
        print('\nOpcion invalida!\n')
        input('Apretar Enter...')

client_socket.close()