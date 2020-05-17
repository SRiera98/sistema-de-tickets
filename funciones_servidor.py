from datetime import datetime
import json
from funciones_DB import guardar_ticket


def almacenar_ticket(sock,lock):
    dict_data = sock.recv(1024).decode('ascii')
    final_data = json.loads(dict_data)
    final_data = dict(final_data)
    for key, value in final_data.items():
        if key == "autor":
            autor = value
        elif key == "titulo":
            titulo = value
        elif key == "descripcion":
            descripcion = value
        elif key == "estado":
            estado = value
    with lock:
        guardar_ticket(autor, titulo, descripcion, estado, fecha=datetime.now())
    sock.send("¡Ticket creado correctamente!\n".encode())
    # for cliente in lista_clientes:
    # if cliente is not sock:
    # cliente.send("¡Se ha creado un nuevo ticket!".encode())