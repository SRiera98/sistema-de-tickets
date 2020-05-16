from modelo import Ticket
from run_DB import session

def listar_tickets():
    """
    Obtiene todos los tickets actuales.
    """
    lista_tickets = session.query(Ticket).all()
    return lista_tickets


def guardar_ticket(autor,titulo,descripcion,estado,fecha):
    """
    Almacena en la BD un ticket
    """
    ticket = Ticket(autor=autor, titulo=titulo, descripcion=descripcion, estado=estado, fecha=fecha)
    session.add(ticket)
    session.commit()
