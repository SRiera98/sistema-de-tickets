from datetime import datetime

def validar_fecha(fecha):
    try:
        opt=datetime.strptime(fecha, "%d-%m-%Y")
        retorno=False
    except ValueError:
        retorno=True
    return retorno

def validar_estado(estado):
    if estado not in ("pendiente", "en procesamiento", "resuelto"):
        retorno=True
    else:
        retorno=False
    return retorno