from datetime import datetime

def validar_fecha(fecha):
    retorno=None
    try:
        opt=datetime.strptime(fecha, "%d-%m-%Y")
        retorno=False
    except ValueError:
        retorno=True
    return retorno