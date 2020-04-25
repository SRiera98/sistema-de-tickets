import csv as csv_fuctions
import getopt
import sys
from datetime import datetime
from zipfile import ZipFile
import os

from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import secure_filename # Modifica el nombre del archivo a uno seguro
from multiprocessing import Process

from modelo import Ticket
from run_DB import session
from validaciones import validar_ticket, validar_numero
import re

def csv_manager(lista_tickets):
    nombre_archivo="track.csv"
    with open(nombre_archivo, "w") as csv_file:
        titulos = ['ticketId', 'fecha', 'titulo', 'autor', 'descripcion', 'estado']
        writer = csv_fuctions.DictWriter(csv_file, fieldnames=titulos)
        writer.writeheader()
        for ticket in lista_tickets:
            writer.writerow({'ticketId': str(ticket.ticketId), 'fecha': str(ticket.fecha), 'titulo': ticket.titulo,
                             'autor': ticket.autor, 'descripcion': ticket.descripcion, 'estado': ticket.estado})
    csv_compress(nombre_archivo)
def csv_compress(filename):
    directorio="CSV_Tickets"
    if not os.path.exists(directorio):
        os.mkdir(directorio)
    nombre_zip=secure_filename("csv ticket - fecha: "+str(datetime.now().strftime("%d-%m-%Y_%H.%M.%S")))
    with ZipFile("CSV_Tickets/"+nombre_zip+".zip", 'w') as zip:
        zip.write(filename)

def procesamiento_csv(tickets):
    proceso=Process(target=csv_manager,args=(tickets,))
    proceso.start()

def menu_edicion(sock,host,port,identificador_ticket):

    ticket_editar = session.query(Ticket).filter(Ticket.ticketId == identificador_ticket).one()

    sock.sendto("\t\t¿Que desea editar?\n\t"
                "1. Editar titulo\n\t"
                "2. Editar estado\n\t"
                "3. Editar descripcion\n\t".encode(), (host, port)) #Enviamos al cliente el MENU
    opcion = sock.recv(1024).decode() #Recibimos la eleccion del cliente.
    if int(opcion) == 1:
        sock.sendto("Ingrese el nuevo titulo a colocar: ".encode(), (host, port))
        nuevo_titulo = sock.recv(1024).decode()
        ticket_editar.titulo = nuevo_titulo
    elif int(opcion) == 2:
        sock.sendto("Ingrese el nuevo estado a colocar: ".encode(), (host, port))
        nuevo_estado = sock.recv(1024).decode()
        ticket_editar.estado = nuevo_estado
    elif int(opcion) == 3:
        sock.sendto("Ingrese la nueva descripcion a colocar: ".encode(), (host, port))
        nueva_descripcion = sock.recv(1024).decode()
        ticket_editar.descripcion = nueva_descripcion
    session.add(ticket_editar)
    session.commit()
    sock.sendto("¡Ticket Editado con Exito!\n".encode(),(host,port))


def parsear_comando(cadena):
    array_comando = []
    array_auxiliar= []
    if re.split("\"",cadena).count("en procesamiento")==0:
        for i in cadena.split(" "):
            print(i)
            array_comando.append(i)
        return array_comando
    else:
        for i in re.split("\"",cadena): #Nos permite parsear un comando cuando se elija "en procesamiento"
            array_comando.append(i)
        for i in array_comando:
            for j in i.split(" "):
                if not j in ("-d","en","procesamiento",''):
                    array_auxiliar.append(j)
        array_auxiliar.append("-d")
        array_auxiliar.append("en procesamiento")
        return array_auxiliar

def validar_comando(cadena):
    retorno=('None',False)
    array_comando = parsear_comando(cadena)
    try:                                                #autor o -a fecha o -f estado o -d
        (opt, arg) = getopt.getopt(array_comando[0:], 'licsxa:f:d:e:', ["listar", "insertar","clear","salir","exportar","autor=","fecha=","estado=","editar="])

        val = False
        filter_dict = dict()
        for opcion, valor in opt:
            if opcion in ('--listar', '-l') and valor == '':
                val = True
                retorno = ('LISTAR', True)
                continue

            if opcion in ('--exportar', '-x') and valor == '':
                val = True
                retorno = ('EXPORTAR', True)
                continue

            if opcion in ('--autor', '-a', '--fecha', '-f', '--estado', '-d') and valor != '' and val is True:
                filter_dict[str(opcion)] = valor

            if opcion in ('--editar', '-e') and validar_numero(valor) is True:
                if validar_ticket(valor) is False:
                    retorno = ('EDITAR', valor)
                else:
                    print("Ticket invalido!")
                    retorno = ('EDITAR', False)

            if opcion in ('--insertar', '-i') and valor == '':
                retorno = ('INSERTAR', True)

            if opcion in ('--clear','-c') and valor == '':
                retorno = ('LIMPIAR',True)

            if opcion in ('--salir', '-s') and valor == '':
                retorno = ('SALIR', True)

            if len(filter_dict) == 0 and opcion in ('--listar', '-l'):
                retorno = ('LISTAR', True)
            elif len(filter_dict) == 0 and opcion in ('--exportar', '-x'):
                retorno= ('EXPORTAR',True)

            if len(filter_dict)>0 and opt.count(('--listar','')) == 1 or opt.count(('-l','')) == 1:
                retorno = ('FILTRAR', filter_dict)
            elif len(filter_dict)>0 and opt.count(('--exportar','')) == 1 or opt.count(('-x','')) == 1:
                retorno=('EXPORTAR',filter_dict)

    except getopt.GetoptError as e:
        print("Error en el comando ingresado, por favor, revise su sintaxis e ingreselo nuevamente.")

    print(f"EL RETORNO ES {retorno}")
    return retorno
