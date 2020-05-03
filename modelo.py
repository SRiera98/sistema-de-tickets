import json

from sqlalchemy import Column, Integer, String, Date, MetaData, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
"""
Los clientes que se conecten podrán, mediante comandos definidos por el programador,
insertar un nuevo ticket, listar los tickets disponibles, y editar el estado de alguno de ellos, y
su información. El listado de tickets deberá contar con un filtro por fecha, autor y estado.
"""


class Ticket(Base):
    __tablename__ = "tickets"
    ticketId = Column(Integer,
                      primary_key=True)  # Column indica que la variable será justamente una columna de la tabla relacional, primary_key: Clave primaria de la tabla para poder relacionarla
    fecha = Column(DateTime, nullable=False)
    titulo = Column(String(60), nullable=False)
    autor = Column(String(60), nullable=False)
    descripcion = Column(String(500), nullable=False)
    estado = Column(String(20), nullable=False)

    def __repr(self):
        return "Ticket: {0}, {1}, {2} {3}".format(self.fecha, self.titulo, self.autor, self.descripcion)

    def __str__(self):
        return f"Identificador: {self.ticketId}\nTitulo: {self.titulo}\nAutor: {self.autor}\nFecha de Creacion: {self.fecha}\nDescripcion: {self.descripcion}\nEstado: {self.estado}\n\n"


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Ticket):
            return {"ticketId": obj.ticketId, "fecha": str(obj.fecha), "titulo": obj.titulo, "autor": obj.autor,
                    "descripcion": obj.descripcion, "estado": obj.estado}
        return json.JSONEncoder.default(self, obj)
