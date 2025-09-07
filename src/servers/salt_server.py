import asyncio
import os
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
import json
from dotenv import load_dotenv

load_dotenv()
lock = asyncio.Lock()

# VARIABLES DE ENTORNO DEL SERVIDOR 
HOST = os.getenv('SALT_HOSTNAME')
PORT = os.getenv('SALT_PORT')
# Conexión a la base de datos
DATABASE_URL = f"mysql+pymysql://{os.getenv('SALTDB_USER')}:{os.getenv('SALTDB_PASSWORD')}@{os.getenv('SALTDB_HOSTNAME')}:{os.getenv('SALTDB_PORT')}/{os.getenv('SALTDB_DATABASE')}"

engine = create_engine(DATABASE_URL)

session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base()

class Salts(Base):
    __tablename__ = 'salts'
    id = Column(Integer, primary_key=True, autoincrement=False)
    salt = Column(LargeBinary, nullable=False)
    
# Crear la tabla en la base de datos
Base.metadata.create_all(bind=engine)

# Función para enviar respuestas del servidor
async def send_message(writer, status, message):
    response = {"status": status, "message": message}
    writer.write(json.dumps(response).encode('utf-8'))
    await writer.drain()

'''Función que procesa las peticiones del servidor: estas pueden
   ser del tipo GET_SALT o SAVE_SALT, según la acción guarda o carga la
   salt de un usuario
'''
async def manage_petition(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Conexión establecida con {addr}")
    ip, port = addr
    if ip == '127.0.0.1':
        try:
            data = await reader.read(1048576)
            if not data:
                return
            message = json.loads(data.decode('utf-8'))
            try:
                message = json.loads(data.decode('utf-8'))
                action = message.get("ACTION")
                if action == "SAVE_SALT":
                    id = message.get("id")
                    salt_hex = message.get("salt")
                    salt = bytes.fromhex(salt_hex)
                    async with lock:
                        session = Session()
                        salt_obj = Salts(id=id, salt=salt)
                        session.add(salt_obj)
                        session.commit()
                        session.close() # Guarda la salt y cierra la sesión
                        response = {"message": "Salt guardado exitosamente"}
                        await send_message(writer, "200", response)
                elif action == "GET_SALT":
                    id = message.get("id")
                    async with lock:
                        session = Session()
                        salt = session.query(Salts).filter_by(id=id).first() # Carga la salt del servidor
                        if salt:
                            salt = salt.salt.hex()
                            response = {"salt": salt}
                            await send_message(writer, "200", response)
                        else:
                            await send_message(writer, "400", "Error")
            except json.JSONDecodeError:
                print("Datos mal formateados recibidos")
                return
        except json.JSONDecodeError:
            print("Datos mal formateados recibidos")


async def main():
    server = await asyncio.start_server(
        manage_petition, HOST, PORT
    )
    addr = server.sockets[0].getsockname()
    print(f"Servidor escuchando en {addr}")

    async with server:
        await server.serve_forever()

# Ejecutar el servidor
asyncio.run(main())