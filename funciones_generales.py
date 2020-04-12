import csv as csv_fuctions
from datetime import datetime
from zipfile import ZipFile
import os

from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import secure_filename # Modifica el nombre del archivo a uno seguro
from multiprocessing import Process

from modelo import Ticket
from run_DB import session


def csv_manager(lista_tickets):
    nombre_archivo="track.csv"
    with open(nombre_archivo, "w") as csv_file:
        titulos = ['ticketId', 'fecha', 'titulo', 'autor', 'descripcion', 'estado']
        writer = csv_fuctions.DictWriter(csv_file, fieldnames=titulos)
        writer.writeheader()
        for ticket in lista_tickets:
            writer.writerow({'ticketId': str(ticket.ticketId), 'fecha': str(ticket.fecha), 'titulo': ticket.titulo,
                             'autor': ticket.autor, 'descripcion': ticket.descripcion, 'estado': ticket.estado})
    csv_compress(nombre_archivo)
def csv_compress(filename):
    directorio="CSV_Tickets"
    if not os.path.exists(directorio):
        os.mkdir(directorio)
    nombre_zip=secure_filename("csv ticket - fecha: "+str(datetime.now()))
    with ZipFile("CSV_Tickets/"+nombre_zip+".zip", 'w') as zip:
        zip.write(filename)

def procesamiento_csv(tickets):
    proceso=Process(target=csv_manager,args=(tickets,))
    proceso.start()

def menu_edicion(sock,host,port,identificador_ticket):
    try:
        ticket_editar = session.query(Ticket).filter(Ticket.ticketId == identificador_ticket).one()
    except NoResultFound:
        sock.sendto("Ticket no encontrado".encode(), (host, port))
        print("Ticket no encontrado.")
    sock.sendto("\t\t¿Que desea editar?\n\t"
                "1. Editar titulo\n\t"
                "2. Editar estado\n\t"
                "3. Editar descripcion\n\t".encode(), (host, port))
    edit_option = sock.recv(1024).decode()
    print(f"edit_option: {edit_option} TYPE {type(edit_option)}\n\n")
    if int(edit_option) == 1:
        sock.sendto("Ingrese el nuevo titulo a colocar: ".encode(), (host, port))
        nuevo_titulo = sock.recv(1024).decode()
        ticket_editar.titulo = nuevo_titulo
    elif int(edit_option) == 2:
        sock.sendto("Ingrese el nuevo estado a colocar: ".encode(), (host, port))
        nuevo_estado = sock.recv(1024).decode()
        ticket_editar.estado = nuevo_estado
    elif int(edit_option) == 3:
        sock.sendto("Ingrese la nueva descripcion a colocar: ".encode(), (host, port))
        nueva_descripcion = sock.recv(1024).decode()
        ticket_editar.descripcion = nueva_descripcion
    session.add(ticket_editar)
    session.commit()