#!/usr/bin/python3
import sys, socket, os
from threading import Thread
from run_DB import session
from modelo import Ticket
from datetime import datetime
from sqlalchemy import func as sql_fuctions
from sqlalchemy.orm.exc import NoResultFound
import json
from validaciones import logger
def thread_fuction(port,sock):
    while True:
        msg = clientsocket.recv(1024)
        print(f"Recibido  del puerto {port} atendido por PID {os.getpid()}:  {msg.decode()}")
        logger(sock,msg)

        if (msg.decode() == 'INSERTAR'):
            dict_data=sock.recv(1024).decode()
            final_data=json.loads(dict_data)
            final_data=dict(final_data)
            for key,value in final_data.items():
                if key == "autor":
                    autor=value
                elif key == "titulo":
                    titulo=value
                elif key == "descripcion":
                    descripcion=value
                elif key == "estado":
                    estado=value
            print(final_data)
            ticket=Ticket(autor=autor,titulo=titulo,descripcion=descripcion,estado=estado,fecha=datetime.now())
            session.add(ticket)
            session.commit()
            break
        elif (msg.decode() == 'LISTAR'):
            pass

        elif (msg.decode() == 'EDITAR'):
            identificador_ticket=sock.recv(1024).decode()
            try:
                ticket_editar=session.query(Ticket).filter(Ticket.ticketId==identificador_ticket).one()
            except NoResultFound:
                sock.sendto("Ticket no encontrado".encode(), (host, port))
                print("Ticket no encontrado.")
            sock.sendto("\t\t¿Que desea editar?\n\t"
                        "1. Editar titulo\n\t"
                        "2. Editar estado\n\t"
                        "3. Editar descripcion\n\t".encode(), (host, port))
            edit_option=sock.recv(1024).decode()
            print(f"edit_option: {edit_option} TYPE {type(edit_option)}\n\n")
            if int(edit_option) == 1:
                sock.sendto("Ingrese el nuevo titulo a colocar: ".encode(), (host, port))
                nuevo_titulo=sock.recv(1024).decode()
                ticket_editar.titulo=nuevo_titulo
            elif int(edit_option) == 2:
                sock.sendto("Ingrese el nuevo estado a colocar: ".encode(), (host, port))
                nuevo_estado = sock.recv(1024).decode()
                ticket_editar.estado = nuevo_estado
            elif int(edit_option) == 3:
                sock.sendto("Ingrese la nueva descripcion a colocar: ".encode(), (host, port))
                nueva_descripcion = sock.recv(1024).decode()
                ticket_editar.descripcion = nueva_descripcion
            session.add(ticket_editar)
            session.commit()

        elif (msg.decode() == 'FILTRAR'):
            pass

        elif (msg.decode() == 'SALIR'):
            break

        else:
            print('\nOpcion invalida!\n')

        if not msg or msg in {""," ",None}:
            break


# creamos el objeto socket
try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Fallo al crear el socket!')
    sys.exit()

#Establecemos parametros
host = "localhost"
port = int(8070)

# Blindeamos el puerto y el host
serversocket.bind((host, port))

# Establecemos 5 peticiones de escucha como maximo.
serversocket.listen(5)
if __name__ == "__main__":
    while True:
        # establish a connection
        clientsocket, addr = serversocket.accept()
        print('Conexion establecida: SERVER ON')
        conection=Thread(target=thread_fuction,args=(port,clientsocket))
        conection.start()

