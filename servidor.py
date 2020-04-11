#!/usr/bin/python3
import sys, socket, os
from threading import Thread,Semaphore
from run_DB import session
from modelo import Ticket
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
import json
from validaciones import logger
from funciones_DB import guardar_ticket
def thread_fuction(port,sock,semaf):
    while True:
        msg = clientsocket.recv(1024)
        print(f"Recibido  del puerto {port} atendido por PID {os.getpid()}:  {msg.decode()}")
        logger(sock,msg)

        if (msg.decode() == 'INSERTAR'):

            dict_data=sock.recv(1024).decode()
            print("dict_data con decode hecho: "+str(dict_data))
            final_data=json.loads(dict_data)
            print("final data antes de ser diccionario: "+str(final_data))
            final_data=dict(final_data)
            print("final data despues de ser diccionario: "+str(final_data))
            for key,value in final_data.items():
                if key == "autor":
                    autor=value
                    print("autor:"+value)
                elif key == "titulo":
                    titulo=value
                    print("titulo:" + value)
                elif key == "descripcion":
                    descripcion=value
                    print("descripcion:" + value)
                elif key == "estado":
                    estado=value
                    print("estado: "+value)
            print(final_data)
            guardar_ticket(autor,titulo,descripcion,estado,fecha=datetime.now())
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
        elif (msg.decode() == 'EXPORTAR'):
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
port = int(8080)

# Blindeamos el puerto y el host
serversocket.bind((host, port))

# Establecemos 5 peticiones de escucha como maximo.
serversocket.listen(5)
if __name__ == "__main__":
    while True:
        # Establecemos el semaforo a utilizar
        semaforo=Semaphore(value=1) #Inicializamos la variable semaforo en 1.
        # Establecemos la conexion
        clientsocket, addr = serversocket.accept()
        print('Conexion establecida: SERVER ON')
        conection=Thread(target=thread_fuction,args=(port,clientsocket,semaforo))
        conection.start()

