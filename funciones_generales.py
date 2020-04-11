import csv as csv_fuctions
from datetime import datetime
from zipfile import ZipFile
import os
from werkzeug.utils import secure_filename # Modifica el nombre del archivo a uno seguro
from multiprocessing import Process
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