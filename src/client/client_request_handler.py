import base64
import socket
import ssl
import json
import os
from dotenv import load_dotenv
import secrets

'''
Este request handler se encarga principalmente del procesamiento de peticiones
al servidor. Está compuesto únicamente por funciones que serán llamadas dentro
del cliente. Las funciones están separadas en 2 por peticion; una para prepara
los datos para su envío (PETICION_data_set_up), la otra se encarga del envío de la petición (request_handler).

En el cliente, a la hora de hacer una petición se realizará de esta manera:
    request_handler(PETICION_data_set_up())
'''
# VARIABLES DE ENTORNO DEL SERVIDOR 
load_dotenv()
HOST = str(os.getenv("SERVER_HOSTNAME"))
PORT = os.getenv("SERVER_PORT")

'''
Lógica de las funciones de data_set_up:
    Los datos se enviaran siempre como un diccionario que contiene todos los datos
    que hacen falta. Dependiendo de la acción a realizar el contenido puede variar, 
    pero siempre debe de contener la pareja "ACTION: ACCION_A_REALIZAR" para que el servidor
    pueda diferenciar que petición está recibiendo y cómo procesarla

    Obviamente cada acción pasa los parámetros oportunos que el servidor necesitará para
    procesar la petición.
'''
# DATA SET UP SECTION
def log_in_data_set_up(self):
        username = self.entry_username.get()
        psswd = self.entry_psswd.get()
        data = {"ACTION": "LOGIN","U": username,"P": psswd}

        return data

def register_data_set_up(self):
    username = self.entry_username.get()
    psswd = self.entry_psswd.get()
    data = {"ACTION": "REGISTER", "U": username, "P": psswd}

    return data


def message_data_set_up(self, username, session_id):
    mesagge = self.entry_message.get()
    data = {"ACTION": "MESSAGE", "U" : username, "M": mesagge, "session_id": session_id} #self.session_id}

    return data

def log_out_data_set_up(session_id, username):
     data = {"ACTION": "LOGOUT", "U": username,"session_id": session_id} # Logout no necesita información
     return data

# REQUEST HANDLER SECTION

'''
Las respuestas del servidor siguen una estructura fija para facilitar su
entendimiento. Los datos se envían como un diccionario de 2 entradas: status y message.

Se usa esta combinación de entradas para facilitar la lectura de las peticiones; utilizando una
estructura semajante a HTTP con los códigos de estados, y un mensaje prefijado para saber que parte del
código se está ejecutando.
'''
def request_handler(data):
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            KEYSTORE_PATH = os.path.join(BASE_DIR, "..", "..", "resources", "server.crt")
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)  # Contexto TLS
            context.load_verify_locations(cafile=KEYSTORE_PATH)
            context.check_hostname = False  # Desactiva verificación de hostname (opcional)

            with socket.create_connection((HOST, PORT)) as sock:
                with context.wrap_socket(sock, server_hostname=HOST) as ssock:  # Envolver en TLS
                    msg = json.dumps(data).encode("utf-8")
                    ssock.sendall(msg)
                    response = ssock.recv(1048576).decode()
                    response = json.loads(response)
                    print("Response: ", response)
                    ssock.close()

                    return response
        except Exception as e:
            print(f"Error en la request: {e}")



        