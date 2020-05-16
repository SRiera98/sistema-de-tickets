from sqlalchemy import func as sql_recursos
from datetime import datetime
from modelo import Ticket
from validaciones import validar_fecha, validar_estado

def filtrar_fecha(lista_tickets,fecha):
    """
    Se encarga de filtrar la lista existente de tickets por la fecha indicada
    :param lista_tickets: Lista obtenida de tipo Query
    :param fecha: String que representa una fecha ingresada por el cliente.
    :return: lista de tickets ya filtrada.
    """
    if validar_fecha(fecha):
        fecha = datetime.strptime(fecha, "%d-%m-%Y").date()
    else:
        print("Formato de fecha incorrecto, ejecute correctamente el comando ")
    lista_tickets = lista_tickets.filter(Ticket.fecha.like(str(fecha) + "%"))
    return lista_tickets

def filtrar_autor(lista_tickets,autor):
    """
    Metodo para filtrar tickets por autor (Ignore Case)
    :param lista_tickets: lista de tickets a filtrar.
    :param autor: String del Autor por el que se desea filtrar.
    :return: lista de tickets filtrada.
    """
    lista_tickets=lista_tickets.filter(sql_recursos.lower(Ticket.autor)==sql_recursos.lower(autor))
    return lista_tickets

def filtrar_estado(lista_tickets,estado):
    """
    Filtrar lista de tickets por estado.
    :param lista_tickets: lista a filtrar.
    :param estado: String que representa el estado.
    :return: lista de tickets filtrada.
    """
    if validar_estado(estado):
        print("Error en el estado ingresado, ejecute nuevamente\n")
    else:
        lista_tickets = lista_tickets.filter(Ticket.estado == estado)
    return lista_tickets

def aplicar_filtro(filtros,lista_tickets):
    """
    Se encarga de la aplicacion de los diversos filtros.
    :param filtros: Diccionario que posee los filtros elegidos por el cliente.
    :param lista_tickets: lista de tickets a aplicar los diversos filtros
    :return: lista de tickets filtrada.
    """
    for clave,valor in filtros.items():
        if clave in ('--autor', '-a'):
            lista_tickets = filtrar_autor(lista_tickets,valor)
        if clave in ('--estado', '-d'):
            lista_tickets = filtrar_estado(lista_tickets,valor)
        if clave in ('--fecha', '-f'):
            lista_tickets = filtrar_fecha(lista_tickets,valor)
    return lista_tickets


