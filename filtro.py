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

def aplicar_filtro(filtros,lista_tickets):
    for filtro in filtros:
        if filtro == "autor":
            lista_tickets = filtrar_autor(lista_tickets)
        if filtro == "estado":
            lista_tickets = filtrar_estado(lista_tickets)
        if filtro == "fecha":
            lista_tickets = filtrar_fecha(lista_tickets)
    return lista_tickets
def mostrar_filtro(lista_tickets):
    if lista_tickets.count() == 0:
        print("No hay resultados para su busqueda!\n")
    else:
        print("Resultados de la busqueda: \n")
        for ticket in lista_tickets:
            print(f"Titulo: {ticket.titulo}\nAutor: {ticket.autor}\nFecha de Creacion: {ticket.fecha}\nDescripcion: {ticket.descripcion}\nEstado: {ticket.estado}\n\n")