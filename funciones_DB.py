from modelo import Ticket
from run_DB import session


def listar_tickets():
    lista_tickets = session.query(Ticket).filter().all()
    print("Los Tickets actuales son: ")
    for ticket in lista_tickets:
        print(f"Identificador: {ticket.ticketId}\nTitulo: {ticket.titulo}\nAutor: {ticket.autor}\nFecha de Creacion: {ticket.fecha}\nDescripcion: {ticket.descripcion}\nEstado: {ticket.estado}\n\n")