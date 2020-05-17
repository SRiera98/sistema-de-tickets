import sys
from validaciones import validar_estado


def ingresar_ticket():
    sys.stdin.flush()  # debemos limpiar el buffer
    autor = input("\nIngrese autor del Ticket: ")
    titulo = input("\nIngrese titulo del ticket: ")
    descripcion = input("\nIngrese descripcion del ticket: ")
    estado = input("\nIngrese estado del ticket (pendiente, en procesamiento o resuelto): ")
    while validar_estado(estado):
        estado = input("Estado debe ser uno de los pedidos, intentelo nuevamente: ")
    data = {"autor": autor, "titulo": titulo, "descripcion": descripcion, "estado": estado}
    return data