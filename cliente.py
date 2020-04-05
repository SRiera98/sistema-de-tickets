import socket, sys
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket Creado!")
except socket.error:
    print ('Fallo al crear el socket!')
    sys.exit()

host = "localhost"
port = int(8050)

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
        - LISTAR TICKET (LISTAR)
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
        estado = input("\nIngrese estado del ticket (pendiente, en procesamiento o resuelto):")

        while estado not in ("pendiente", "en procesamiento", "resuelto"):
            estado=input("Estado debe ser uno de los pedidos, intentelo nuevamente")
        client_socket.sendto(estado.encode(), (host, port))

    elif (opcion == 'LISTAR'):
        print(client_socket.recv(1024).decode())
        while True:
            msg = input()
            client_socket.sendto(msg.encode(), (host, port))
            if msg == 'quit':
                break

    elif (opcion == 'SALIR'):
        break

    else:
        print('\nOpcion invalida!\n')
        input('Apretar Enter...')

    """
    if msg.decode() == 'exit':
        break
    else:
        try :
            #Set the whole string
            client_socket.sendto(msg, (host, port))
        except socket.error:
            #Send failed
            print ('Fallo al enviar el msg!')
            sys.exit()"""

client_socket.close()