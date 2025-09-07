import os
import sys
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import socket
import ssl
import threading
import json
import signal
import asyncio
from dotenv import load_dotenv
from database.setup_database import database_setup
from server_request_handler import *
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, BestAvailableEncryption
from cryptography.hazmat.backends import default_backend


load_dotenv()

lock = asyncio.Lock()
stop_event = asyncio.Event()
# Diccionario para el manejo de sesiones
sessions_log = dict()

'''
Lógica del manejo de la sesión:
        Una vez creada la sesión mediante log_in o register; la respuesta deberá devolver
        en el campo "message" una id de la sesión. Esta deberá ser enviada en todos los mensajes
        para que el servidor compruebe la sesión. En caso de que la sesion id no esté registrada,
        el cliente se cerrará

        El servidor manejará la sesión almacenandola en un diccionario de manera temporal y 
        comprobando que las credenciales de la sesión coinciden al recibir un mensaje. Log_out elimina
        la sesión del diccionario.
'''

# Session se usa para la conexión a la base de datos
async def handle_client(conn, addr, Session):
    print(f"Conexión establecida con: {addr}")
    
    with conn:
        data = conn.recv(1024).decode('utf-8')
        print(f"Mensaje recibido: {data}")

        message = json.loads(data)
        action = message.get("ACTION")
        response = {"status": "400", "message": "Acción no válida"}

        try:
            if action == "LOGIN":
                response = await log_in_server_logic(Session, lock, message)
                sessions_log[response.get("message")] = message.get("U") # Registrar la sesión

            if action == "REGISTER":
                response =  await register_server_logic(Session, lock, message)
                sessions_log[response.get("message")] = message.get("U") # Registrar la sesión

            if action == "MESSAGE":
                response = await message_server_logic(Session, lock, message, sessions_log)

            if action == "LOGOUT":
                response = log_out_server_logic(message)
                del sessions_log[message.get("session_id")]

            response_json = json.dumps(response).encode('utf-8')
            conn.sendall(response_json)
            print(f"Respuesta enviada: {response}")
        
        except Exception as e:
            print(f"Error en la conexión con el cliente: {e}")
            conn.sendall(json.dumps({"status": "500", "message": "Error interno del servidor"}).encode('utf-8'))

    print(f"Conexión cerrada con: {addr}")

def start_ssl_server():
    host = str(os.getenv("SERVER_HOSTNAME"))
    port = int(os.getenv("SERVER_PORT"))
   
    Session = database_setup()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor SSL escuchando en el puerto {port}...")


    # 1. Cargar el keystore.p12
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    KEYSTORE_PATH = os.path.join(BASE_DIR, "..", "..", "resources", "keystore.p12")
    with open(KEYSTORE_PATH, "rb") as p12_file:
        p12_data = p12_file.read()


    # 2. Extraer la clave privada, el certificado y (opcional) otros certificados
    private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
        p12_data,
        os.getenv("KEYSTORE_PASSWORD").encode("utf-8"),
        default_backend()
    )


    # 3. Crear un archivo temporal con la clave y el certificado en formato PEM
    with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as temp_key_cert_file:
        pem_private_key = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=BestAvailableEncryption(os.getenv("KEYSTORE_PASSWORD").encode("utf-8"))
        )
        pem_cert = certificate.public_bytes(Encoding.PEM)
       
        # IMPORTANTE: Escribir primero el certificado y luego la clave privada.
        temp_key_cert_file.write(pem_cert)
        temp_key_cert_file.write(pem_private_key)
        temp_key_cert_path = temp_key_cert_file.name


    # 4. Configurar el SSLContext para el servidor
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=temp_key_cert_path, keyfile=temp_key_cert_path)
    ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3


    with ssl_context.wrap_socket(server_socket, server_side=True) as ssl_socket:
        while True:
            conn, addr = ssl_socket.accept()
            client_thread = threading.Thread(target=lambda: asyncio.run(handle_client(conn, addr, Session)))
            client_thread.start()


if __name__ == "__main__":
    start_ssl_server()

