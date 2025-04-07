from db import app, mysql, mail
from flask_mail import Mail, Message

def enviar_correo(tipo=None ,usuario = None,contenido = None):
    if tipo == 'registro':
        msg = Message('¡Hola desde Flask!',
                sender='contacto.soydongalleto@gmail.com',
                recipients=['johan.antonio25@gmail.com'])
        msg.body = 'Este es un mensaje enviado desde una app Flask.'
        mail.send(msg)
    return 'Correo enviado'

    return 'Correo enviado'