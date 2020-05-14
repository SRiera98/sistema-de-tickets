from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from modelo import Ticket
from run_DB import session
from os import system
from IPy import IP

def validar_fecha(fecha):
    """
    Comprueba si el String fecha es valido.
    :param fecha: String que representa una posible fecha.
    :return: True cuando la fecha tiene el formato DD-MM-YYYY, False cuando no.
    """
    try:
        opt = datetime.strptime(fecha, "%d-%m-%Y")
        retorno = True
    except ValueError:
        retorno = False
    return retorno


def validar_estado(estado):
    """
    Comprueba si el estado de ticket es valido.
    :param estado: String que representa un estado de ticket.
    :return: True cuando es incorrecto, False cuando no lo es.
    """
    if estado not in ("pendiente", "en procesamiento", "resuelto"):
        retorno = True
    else:
        retorno = False
    return retorno


def validar_ticket(id_ticket):
    """
    Comprueba si el ID del ticket existe en la BD o no.
    :return: True cuando existe, False cuando no existe.
    """
    try:
        session.query(Ticket).filter(Ticket.ticketId == id_ticket).one()
        retorno = True
    except NoResultFound:
        retorno = False
    return retorno


def validar_numero(numero):
    """
    Comprueba si el valor es un entero.
    :param numero: valor a comprobar si es numerico.
    :return: retorno: el cual es True cuando es un valor entero, y False cuando no lo es.
    """
    retorno = None
    try:
        if isinstance(int(numero), int):
            retorno = True
    except ValueError:
        print("Error de valor")
        retorno = False
    return retorno


def logger(sock, msg):
    """
    Este metodo se encarga de abrir el archivo de log para guardar la opcion ingresada por el usuario.
    :param sock: socket de un cliente conectado.
    :param msg: opcion ingresada por el cliente.
    :return: Nada.
    """
    if msg.decode() in ("INSERTAR", "LISTAR", "FILTRAR", "EDITAR", "LIMPIAR", "EXPORTAR", "SALIR"):
        with open("log", "a+") as file:
            ip, port = sock.getpeername()
            fecha = datetime.now().strftime("%d-%m-%Y %H h:%M min:%S seg")
            file.write(f"Dirección IP Cliente: {ip} - Fecha: {fecha} - Operacion ejecutada: {msg.decode()}\n")


def clear_screen():
    """
    Limpia la pantalla usando el comando de Sistema "clear"
    """
    system('clear')

def validar_ip(ip):
    """
    Comprueba formato IP.
    :param ip: IP ingresada al momento de conectar el cliente.
    :return: True cuando esa IP es valida (checkea formato y si se pasa de 255), False cuando hay un error.
    """
    retorno=None
    try:
        IP(str(ip))
        retorno=True
    except ValueError:
        retorno=False
    return retorno
