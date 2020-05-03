from modelo import Ticket
from run_DB import session

def listar_tickets():
    lista_tickets = session.query(Ticket).all()
    return lista_tickets
"""    print("Los Tickets actuales son: ")
    for ticket in lista_tickets:
        print(f"Identificador: {ticket.ticketId}\nTitulo: {ticket.titulo}\nAutor: {ticket.autor}\nFecha de Creacion: {ticket.fecha}\nDescripcion: {ticket.descripcion}\nEstado: {ticket.estado}\n\n")
    """

def guardar_ticket(autor,titulo,descripcion,estado,fecha):
    ticket = Ticket(autor=autor, titulo=titulo, descripcion=descripcion, estado=estado, fecha=fecha)
    session.add(ticket)
    session.commit()
