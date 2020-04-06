import socket, sys
from modelo import Ticket
from run_DB import session

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
    """
    objeto = Ticket()
    objeto.autor = "Josawdwawadwdwadadwe"
    objeto.titulo = "Fork bawdawdaddwaomb"
    objeto.fecha = datetime.now()
    objeto.descripcion = "descripcion probando neiegoa sawdawdwadwadwdae fue al carajo todo ameo"
    objeto.estado = "resuelto"

    
    session.add(objeto)
    session.commit()"""
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
        lista_tickets=session.query(Ticket).filter(Ticket.estado=="pendiente")
        print("Los Tickets actuales sin resolver son: ")
        for ticket in lista_tickets:
            print(f"Titulo: {ticket.titulo}\nAutor: {ticket.autor}\nFecha de Creacion: {ticket.fecha}\nDescripcion: {ticket.descripcion}\nEstado: {ticket.estado}\n\n")

    elif (opcion == 'SALIR'):
        break

    else:
        print('\nOpcion invalida!\n')
        input('Apretar Enter...')

client_socket.close()