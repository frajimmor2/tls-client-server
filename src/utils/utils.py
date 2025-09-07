import secrets
import hashlib
import socket
import threading
import json
import ssl
from dotenv import load_dotenv
import os
import hmac

load_dotenv()

def hash_password(password: str):
    salt = secrets.token_bytes(16)  # Genera un salt aleatorio de 16 bytes
    password_bytes = password.encode('utf-8')  # Convierte la contraseña a bytes
    hash_obj = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 600000)  # Aplica SHA-256 con iteraciones
    return hash_obj, salt

def verify_password(password: str, salt: bytes, stored_hash: bytes) -> bool:
    password_bytes = password.encode('utf-8')
    new_hash = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 600000)
    return hmac.compare_digest(new_hash, stored_hash)


def save_salt_in_salt_server(user_id, salt):
    data = {
        "ACTION": "SAVE_SALT",
        "id": user_id,
        "salt": salt.hex()
    }
    threading.Thread(target=save_salt_in_salt_server_request, args=(data,), daemon=True).start()

def save_salt_in_salt_server_request(data):
    s = None
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((os.getenv("SERVER_HOSTNAME"),int(os.getenv("SALT_PORT_SOURCE"))))
            s.connect((os.getenv("SALT_HOSTNAME"),int(os.getenv("SALT_PORT"))))
            msg = json.dumps(data).encode("utf-8")
            s.sendall(msg)
            response = s.recv(1048576).decode()
            response = json.loads(response)
            status = response.get("status")
            print("Save salt response:", response)
            if status != "200":
                raise Exception("Error al guardar la salt")
    except Exception as e:
        print(f"Error en save_salt_in_salt_server_request: {e}")
        raise
    finally:
        if s:
            s.close()
        

def get_salt_from_salt_server(user_id):
    data = {
        "ACTION": "GET_SALT",
        "id": user_id
    }
    return get_salt_from_salt_server_request(data)

def get_salt_from_salt_server_request(data):
    
    try:

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)  # Contexto TLS
        context.check_hostname = False  # Desactiva verificación de hostname (opcional)
        context.verify_mode = ssl.CERT_NONE  # No verifica el certificado (puedes cambiar esto)
        
        with socket.create_connection(('127.0.0.1', 20002)) as sock:
                
            msg = json.dumps(data).encode("utf-8")
            sock.sendall(msg)
            response = sock.recv(1048576).decode()
            response = json.loads(response)
            sock.close()
            if response.get("status") == "200":
                return bytes.fromhex(response["message"]["salt"])
            else:
                return 0

    except Exception as e:
        print(f'Error al pedir la salt: {e}')