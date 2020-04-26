from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from modelo import Ticket
from run_DB import session
from os import system


def validar_fecha(fecha):
    try:
        opt = datetime.strptime(fecha, "%d-%m-%Y")
        retorno = False
    except ValueError:
        retorno = True
    return retorno


def validar_estado(estado):
    if estado not in ("pendiente", "en procesamiento", "resuelto"):
        retorno = True
    else:
        retorno = False
    return retorno


def validar_ticket(id_ticket):
    try:
        session.query(Ticket).filter(Ticket.ticketId == id_ticket).one()
        retorno = False
    except NoResultFound:
        retorno = True
    return retorno


def validar_numero(numero):
    retorno = None
    try:
        if isinstance(int(numero), int):
            retorno = True
    except ValueError:
        print("Has ingresado una letra!")
        retorno = False
    return retorno


def logger(sock, msg):
    if msg.decode() in ("INSERTAR", "LISTAR", "FILTRAR", "EDITAR", "LIMPIAR", "EXPORTAR", "SALIR"):
        with open("log", "a+") as file:
            ip, port = sock.getpeername()
            fecha = datetime.now().strftime("%d-%m-%Y %H h:%M min:%S seg")
            file.write(f"Dirección IP Cliente: {ip} - Fecha: {fecha} - Operacion ejecutada: {msg.decode()}\n")


def clear_screen():
    system('clear')
