import csv as csv_fuctions
from funciones_DB import listar_tickets
def csv_manager():
    lista_tickets=listar_tickets()
    csv=open("track.csv","w")
    csv_writer=csv_fuctions.writer(csv)
    csv_head="ticketId,fecha,titulo,autor,descripcion,estado\n"
    #csv_writer.writerow([csv_head])
    csv.write(csv_head)

    for ticket in lista_tickets:
        """
        >> > import csv
        >> > spamWriter = csv.writer(open('eggs.csv', 'wb'))
        >> > spamWriter.writerow(['Spam', 'Lovely, Spam'])"""
        fila="'"+str(ticket.ticketId)+"'"+","+"'"+str(ticket.fecha)+"'"+","+"'"+ticket.titulo+"'"+","+"'"+ticket.autor+"'"+","+"'"+ticket.descripcion+"'"+","+"'"+ticket.estado+"\n"
        csv.write(fila)
        #csv_writer.writerow([fila])
    csv.close()
csv_manager()