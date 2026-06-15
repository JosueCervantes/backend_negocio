#archivo para centralizar la conexion a la base de datos

from sqlmodel import create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
        #yield sirve para que una función entregue un valor, pero se quede en pausa y luego pueda continuar para limpiar la sesión