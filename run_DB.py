from modelo import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv
from dotenv import load_dotenv

load_dotenv()  # Parsea el archivo .env y luego carga todas sus variables como variables de entorno.

# Configuramos motor de BD
engine = create_engine(f"mysql+pymysql://{getenv('DB_USERNAME')}:{getenv('DB_PASS')}@192.168.0.106/{getenv('DB_NAME')}")

# Creamos las Tablas
Base.metadata.create_all(engine)

# Creamos una instancia de session maker
Session = sessionmaker(bind=engine)

# Creamos la sesion, nos permite el manejo de la BD.
session = Session()
