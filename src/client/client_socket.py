#!/usr/bin/env python3
import base64
import hashlib
import hmac
import secrets
import tkinter as tk
from tkinter import messagebox
import socket
import json
import threading
import ssl
from client_request_handler import *


class ClientSocket:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interfaz para cliente")
        self.root.geometry("400x300")
        self.first_view()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.root.mainloop()

    '''
    Lógica de las vistas del pop-up:
        La vista inicial tiene 2 opciones, registrarse e iniciar sesión. Al pulsar sus botones
        se llama a una función auxiliar que ejecuta la petición con el servidor.La función decide si,
        en caso positivo pasa a la siguiente vista disponible o, en caso negativo, muestra un mensaje
        de error

        En la vista posterior del envío de mensajes; el sistema permitirá o enviar mensajes o cerrar sesión

        En todos los casos de uso negativos ya sea un inicio de sesión con contraseña incorrecta;
        resgistro de un usuario ya existente, mensaje demasiado largo, etc, el sistema reacciona
        enviando un pop-up con un mensaje adecuado a la situación
    '''
    def first_view(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        tk.Label(self.root, text="Nombre de usuario").pack()
        self.entry_username = tk.Entry(self.root)
        self.entry_username.pack()
        tk.Label(self.root, text="Contraseña").pack()
        self.entry_psswd = tk.Entry(self.root, show="*")
        self.entry_psswd.pack()
        tk.Button(self.root, text="Iniciar sesión", command= self.log_in).pack()
        tk.Button(self.root, text="Registrarse", command= self.register).pack()
        #self.setup_dh()
    
    '''
    Lógica de las funciones de transacciones:
        Los datos se enviaran siempre como un diccionario que contiene todos los datos
        que hacen falta. Dependiendo de la acción a realizar el contenido puede variar, 
        pero siempre debe de contener la pareja "ACTION: ACCION_A_REALIZAR" para que el servidor
        pueda diferenciar que petición está recibiendo y cómo procesarla

        Obviamente cada acción pasa los parámetros oportunos que el servidor necesitará para
        procesar la petición

    Lógica del manejo de la sesión:
        Una vez creada la sesión mediante log_in o register; la respuesta deberá devolver
        en el campo "message" una id de la sesión. Esta deberá ser enviada en todos los mensajes
        para que el servidor compruebe la sesión. En caso de que la sesion id no esté registrada,
        el cliente se cerrará
    '''
    
    
    def log_in(self):
        username = self.entry_username.get()
        response = request_handler(log_in_data_set_up(self)) # Llama al handler para hacer la petición

        if response.get("status") == "200": # En caso positivo procesa todo y pasa a la siguiente vista
            messagebox.showinfo("Bienvenido","Has iniciado sesión") # Mensaje de bienvenida por inicio de sesión
            self.root.after(0, lambda: self.messages_view(username, response.get("message"))) # Pasa la sesion_id a la siguiente vista
        else: 
            self.root.after(0, lambda: messagebox.showwarning("Error", "Usuario y contraseña incorrectos")) # En caso negativo Pop-up de error
        

    

    def register(self):
        username = self.entry_username.get()
        response = request_handler(register_data_set_up(self)) # Llama al handler para hacer la petición


        if response.get("status") == "200": # En caso positivo procesa todo y pasa a la siguiente vista
            messagebox.showinfo("Bienvenido","¡Registrado con éxito!") # Requisito de que se envíe un mensaje de confirmación de registro
            self.root.after(0, lambda: self.messages_view(username, response.get("message"))) # Pasa la sesion_id a la siguiente vista
        else:
            self.root.after(0, lambda: messagebox.showwarning("Error", "No se pudo registrar el usuario, ya exite uno con ese nombre")) # En caso negativo Pop-up de error



    def messages_view(self, username, session_id):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.root.title(f"Cuenta de: {username}")
        tk.Label(self.root, text="Introduzca su mensaje").pack()
        self.entry_message = tk.Entry(self.root)
        self.entry_message.pack()
        tk.Button(self.root, text="Enviar mensaje", command=lambda: self.send_message(username, session_id)).pack()
        tk.Button(self.root, text="Cerrar sesión", command=lambda: self.log_out(session_id, username)).pack() 
    
    def send_message(self, username, session_id):
        # Primero se debe de cumplir la validación de los mensajes
        message = self.entry_message.get()

        if(len(message) > 144): # Como solo es una validación no es necesario implementar una función que la evalúe
            self.root.after(0, lambda: messagebox.showwarning("Error", "No se pueden enviar mensajes de más de 144 caracteres"))
        else:
            response = request_handler(message_data_set_up(self, username, session_id)) # Llama al handler para hacer la petición

            if response.get("status") == "200":
                self.root.after(0, lambda: messagebox.showinfo("OK", "Mensaje enviado y recibido correctamente")) # En caso positivo, Pop-up de confirmación
            elif response.get("status") == "403":
                self.close_app()
                messagebox.showwarning("Error", "Problema con la sesión, iniciela de nuevo")
            else:
                self.root.after(0, lambda: messagebox.showwarning("Error", "No se pudo enviar el mensaje")) # En caso negativo Pop-up de error


    def log_out(self, session_id, username):
        request_handler(log_out_data_set_up(session_id, username)) # Solo hace falta llamar al handler con el logout
        # Cierra la aplicación (y en este caso no se reinicia la interfaz)
        self.close_app()

    def close_app(self):
        """Cierra la ventana de la aplicación, terminando la sesión del cliente."""
        self.root.destroy()
        # Opcionalmente, se puede forzar la salida del programa:
        # import sys
        # sys.exit(0)
              
if __name__ == "__main__":
    ClientSocket()
