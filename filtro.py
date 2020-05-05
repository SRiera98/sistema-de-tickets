import os
import sys
from sqlalchemy import func as sql_recursos
from datetime import datetime
from modelo import Ticket
from validaciones import validar_fecha

def mostrar_menu_filtro():
    exit = False
    entry = 0
    filtros = list()
    test = "yes"
    while not exit and entry < 3:
        filtro = input("Ingrese el tipo de filtro por el que desea comenzar (fecha, autor o estado):").lower()
        while filtro not in ("fecha", "autor", "estado"):
            filtro = input("Filtro incorrecto, intentelo nuevamente: ")
        filtros.append(filtro)
        if entry < 2 and test == "yes":
            test = input("¿Desea añadir otro filtro? (yes/no): ")
            entry += 1
            exit = False
            if test == "no":
                exit = True
        else:
            exit = True
    return filtros
def filtrar_fecha(lista_tickets,fecha):
    #fecha=input("Ingrese la fecha por la que desea buscar (formato DD-MM-YYYY): ")
    if validar_fecha(fecha) is False:
        fecha = datetime.strptime(fecha, "%d-%m-%Y").date()
    else:
        print("Formato de fecha incorrecto, ejecute correctamente el comando: ")
    lista_tickets = lista_tickets.filter(Ticket.fecha.like(str(fecha) + "%"))
    return lista_tickets

def filtrar_autor(lista_tickets,autor):
    #autor=input("Ingrese el autor por el que desea filtrar: ")
    lista_tickets=lista_tickets.filter(sql_recursos.lower(Ticket.autor)==sql_recursos.lower(autor))
    return lista_tickets

def filtrar_estado(lista_tickets,estado):
    #estado = input("Ingrese el estado por el que desea filtrar: ")
    if estado not in ("pendiente", "en procesamiento", "resuelto"):
        print("Error en el estado ingresado, ejecute nuevamente\n")
    else:
        lista_tickets = lista_tickets.filter(Ticket.estado == estado)
    return lista_tickets

def aplicar_filtro(filtros,lista_tickets):
    for clave,valor in filtros.items():
        if clave in ('--autor', '-a'):
            lista_tickets = filtrar_autor(lista_tickets,valor)
        if clave in ('--estado', '-d'):
            lista_tickets = filtrar_estado(lista_tickets,valor)
        if clave in ('--fecha', '-f'):
            lista_tickets = filtrar_fecha(lista_tickets,valor)
    return lista_tickets


