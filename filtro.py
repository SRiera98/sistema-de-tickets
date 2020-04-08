from datetime import datetime
from modelo import Ticket
from validaciones import validar_fecha


def filtrar_fecha(lista_tickets):
    fecha=input("Ingrese la fecha por la que desea buscar (formato DD-MM-YYYY): ")
    while validar_fecha(fecha):
        fecha = input("Formato de fecha incorrecto, intentelo nuevamente: ")
    fecha = datetime.strptime(fecha, "%d-%m-%Y").date()
    lista_tickets = lista_tickets.filter(Ticket.fecha.like(str(fecha) + "%"))
    return lista_tickets

def filtrar_autor(lista_tickets):
    autor=input("Ingrese el autor por el que desea filtrar: ")
    lista_tickets=lista_tickets.filter(Ticket.autor==autor)
    return lista_tickets

def filtrar_estado(lista_tickets):
    estado = input("Ingrese el estado por el que desea filtrar: ")
    while estado not in ("pendiente", "en procesamiento", "resuelto"):
        estado=input("Error al ingresar el estado, intentelo nuevamente: ")
    lista_tickets = lista_tickets.filter(Ticket.estado == estado)
    return lista_tickets