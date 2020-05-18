import csv as csv_fuctions
import getopt
import socket
import sys
from datetime import datetime
from zipfile import ZipFile
import os
from werkzeug.utils import secure_filename # Modifica el nombre del archivo a uno seguro
from multiprocessing import Process
from modelo import Ticket
from run_DB import session
from validaciones import validar_ticket, validar_numero, validar_ip, validar_fecha, validar_estado
import re

def csv_manager(lista_tickets):
    """
    Se encarga de la creacion del CSV, y llama a csv_compress para comprimirlo.
    :param lista_tickets: lista de tipo Query, Se utilizara para recorrerla e ir escribiendo el .CSV.
    :return: Nada.
    """
    nombre_archivo="track.csv"
    with open(nombre_archivo, "w") as csv_file:
        titulos = ['ticketId', 'fecha', 'titulo', 'autor', 'descripcion', 'estado']
        writer = csv_fuctions.DictWriter(csv_file, fieldnames=titulos)
        writer.writeheader()
        for ticket in lista_tickets:
            writer.writerow({'ticketId': str(ticket.ticketId), 'fecha': str(ticket.fecha), 'titulo': ticket.titulo,
                             'autor': ticket.autor, 'descripcion': ticket.descripcion, 'estado': ticket.estado})
    csv_compress(nombre_archivo)
def csv_compress(archivo):
    """
    Comprime y almacena en un directorio el CSV creado en csv_manager.
    :param archivo: Nombre de archivo a comprimir en .zip
    :return: Nada
    """
    directorio="CSV_Tickets"
    if not os.path.exists(directorio):
        os.mkdir(directorio)
    nombre_zip=secure_filename("csv ticket - fecha: "+str(datetime.now().strftime("%d-%m-%Y_%H.%M.%S")))
    with ZipFile(directorio+"/"+nombre_zip+".zip", 'w') as zip:
        zip.write(archivo)

def procesamiento_csv(tickets):
    """
    Se encarga de lanzar un Proceso para realizar el trabajo de exportacion de tickets.
    :param tickets: Lista de tickets tipo Query a exportar.
    :return: Nada
    """
    proceso=Process(target=csv_manager,args=(tickets,))
    proceso.start()

def menu_edicion(sock,identificador_ticket):
    """
    Encargado de la edicion del ticket
    :param sock: socket que representa un cliente.
    :param identificador_ticket: ID de un ticket
    :return: Nada
    """
    sys.stdin.flush()
    ticket_editar = session.query(Ticket).filter(Ticket.ticketId == identificador_ticket).one()
    sock.send("\t\t¿Que desea editar?\n\t"
                "1. Editar titulo\n\t"
                "2. Editar estado\n\t"
                "3. Editar descripcion\n\t".encode()) #Enviamos al cliente el MENU
    opcion = sock.recv(1024).decode('ascii') #Recibimos la eleccion del cliente.
    if int(opcion) == 1:
        sock.send("Ingrese el nuevo titulo a colocar: ".encode('ascii'))
        nuevo_titulo = sock.recv(1024).decode()
        ticket_editar.titulo = nuevo_titulo
    elif int(opcion) == 2:
        sock.send("Ingrese el nuevo estado a colocar: ".encode('ascii'))
        nuevo_estado = sock.recv(1024).decode()
        ticket_editar.estado = nuevo_estado
    elif int(opcion) == 3:
        sock.send("Ingrese la nueva descripcion a colocar: ".encode('ascii'))
        nueva_descripcion = sock.recv(1024).decode()
        ticket_editar.descripcion = nueva_descripcion
    session.add(ticket_editar)
    session.commit()
    sock.send("¡Ticket Editado con Exito!\n".encode())


def parsear_comando(cadena):
    """
    Se encarga de controlar el caso especial cuando tenemos que pasar como opcion de comando el estado "en procesamiento"
    :param cadena: El comando ingresado por el usuario, que se utilizara en validar_comando
    :return: Array de String que podra ser procesado por GetOpt.
    """
    array_comando = []
    array_auxiliar= []
    if re.split("\"",cadena).count("en procesamiento")==0:
        for i in cadena.split(" "):
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
    """
    Se encarga de validar el comando ingresado por el cliente mediante GetOpt.
    :param cadena: El comando.
    :return: Una tupla cuyo primer valor es un String de la Opción ingresada, el segundo es un un Boolean o un Filtro.
    """
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
                if validar_ticket(valor) is True:
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
    return retorno
def controlar_ejecucion_cliente():
    """
    Se encarga de parsear los parametros pasados al momento de iniciar el cliente.
    :return: El host y el puerto con el cual el socket se conectará.
    """
    host=None
    port=None
    try:
        (opt, arg) = getopt.getopt(sys.argv[1:], 'h:p:', ["host=","puerto="])
        for opcion, valor in opt:
            if opcion in ("-p", "--puerto") and validar_numero(valor) is True:
                port = int(valor)
            if opcion in ("-h","--host") and (valor in ("localhost","") or validar_ip(valor) is True):
                host=valor
    except getopt.GetoptError as e:
        print("¡Debe especificar el host y puerto!")
        sys.exit(1)
    return (host,port)

def control_ejecucion_servidor():
    # Establecemos host y puerto.
    port = None
    try:
        (opt, arg) = getopt.getopt(sys.argv[1:], 'p:', ["puerto="])
        for opcion, valor in opt:
            if opcion in ("-p", "--puerto") and validar_numero(valor) is True:
                port = int(valor)
    except getopt.GetoptError as e:
        print("La estructura de comando es incorrecta.")
        sys.exit(1)
    return port

def control_filtro(test):
    """
    :param test: Posible filtro ingresado.
    :return: False si el estado y fecha son validos sintacticamente, True si no lo son.
    """
    control_fecha = None
    control_estado = None
    if test is not True:
        for k, v in test.items():
            if k in ('--fecha', '-f'):
                control_fecha = validar_fecha(v)
            elif k in ('--estado', '-d'):
                control_estado = validar_estado(v)
    if control_fecha is False or control_estado:
        print("La sintaxis de filtros ha fallado, ejecute nuevamente el comando.")
        retorno=True
    else:
        retorno=False
    return retorno

def control_creacion_ticket(client_socket):
    try:
        client_socket.settimeout(0.2)
        aviso = client_socket.recv(32).decode()
        if aviso == "¡Se ha creado un nuevo ticket!":
            print(aviso)
        else:
            pass

        client_socket.settimeout(None)
        client_socket.setblocking(True)  # son lo mismo.
    except socket.timeout:
        client_socket.settimeout(None)
        client_socket.setblocking(True)