#!/usr/bin/python3
from multiprocessing import Lock
import sys, socket, os
from threading import Thread

from funciones_generales import menu_edicion
from run_DB import session
from modelo import Ticket
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
import json
from validaciones import logger
from funciones_DB import guardar_ticket
import time
def thread_fuction(port,sock,lista_clientes,i):
    while True:
        msg = clientsocket.recv(1024)
        print(f"Recibido  del puerto {port} atendido por PID {os.getpid()}:  {msg.decode()}")
        logger(sock,msg)

        if (msg.decode() == 'INSERTAR'):
            with lock:

                dict_data=sock.recv(1024).decode()
                #print("dict_data con decode hecho: "+str(dict_data))
                final_data=json.loads(dict_data)
                #print("final data antes de ser diccionario: "+str(final_data))
                final_data=dict(final_data)
                #print("final data despues de ser diccionario: "+str(final_data))

                for key,value in final_data.items():
                    if key == "autor":
                        autor=value
                        #print("autor:"+value)
                    elif key == "titulo":
                        titulo=value
                        #print("titulo:" + value)
                    elif key == "descripcion":
                        descripcion=value
                        #print("descripcion:" + value)
                    elif key == "estado":
                        estado=value
                        #print("estado: "+value)
                print(final_data)
                guardar_ticket(autor,titulo,descripcion,estado,fecha=datetime.now())
            #for ip,puerto in lista_clientes:
                #ip_actual,puerto_actual=sock.getpeername()
                #if not puerto_actual==puerto:
                    #sock.sendto(f"El cliente de Puerto {puerto_actual} agrego un ticket!".encode(), (host, puerto))
            break
        elif (msg.decode() == 'LISTAR'):
            pass

        elif (msg.decode() == 'EDITAR'):

            identificador_ticket=sock.recv(1024).decode()
            lista_ids_edicion.append(identificador_ticket)
            if lista_ids_edicion.count(identificador_ticket)>=2:
                if i is True:
                    print("Se esta editando ese ticket") #TERMINAR
                    menu_edicion(sock, host, port, identificador_ticket)
            else:
                i = lock.acquire()
                print(f"El valor de i es: {i}")
                menu_edicion(sock, host, port, identificador_ticket)
                lock.release()
            lista_ids_edicion.remove(identificador_ticket)
            break


        elif (msg.decode() == 'FILTRAR'):
            pass
        elif (msg.decode() == 'EXPORTAR'):
            pass
        elif (msg.decode() == 'SALIR'):
            for ip, puerto in lista_clientes:
                ip_actual, puerto_actual = sock.getpeername()
                if puerto_actual == puerto:
                    lista_clientes.remove((ip,puerto))
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
    lista_clientes = list() #Lista que tiene los clientes actuales.
    lista_ids_edicion=list()
    lock = Lock()
    while True:
        # Establecemos la conexion
        clientsocket, addr = serversocket.accept()
        lista_clientes.append(clientsocket.getpeername())
        print('Conexion establecida: SERVER ON')
        i = 0
        conection=Thread(target=thread_fuction,args=(port,clientsocket,lista_clientes,i))
        conection.start()
