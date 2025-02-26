from modelosdb import Usuario
from peewee import IntegrityError, DoesNotExist
import logging

# Diccionario para almacenar usuarios registrados
usuarios = {}

# Función para cargar usuarios desde la base de datos al inicio
def cargar_usuarios():
    try:
        
        for usuario in Usuario.select():
            usuarios[usuario.chat_id] = {
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'correo' : usuario.correo,
                'area': usuario.area
            }
    except Exception as e:
        logging.error(f'Error al cargar usuarios desde la base de datos: {e}')


# Cargar usuarios al iniciar el bot
cargar_usuarios()

# Función para guardar datos de usuario en la base de datos
def guardar_datos_usuario(chat_id, usuario):
    try:
        nuevo_usuario = Usuario.create(
            chat_id=chat_id,
            nombre=usuario['nombre'],
            apellido=usuario['apellido'],
            correo=usuario['correo'],
            area=usuario['area'],
            telefono=usuario['telefono']
        )
        usuarios[chat_id] = {
            'nombre': nuevo_usuario.nombre,
            'apellido': nuevo_usuario.apellido,
            'correo' : nuevo_usuario.correo,
            'area': nuevo_usuario.area
        }
        print(f'Nuevo Usuario añadido en la base de datos: {usuario["nombre"]} {usuario["apellido"]} (Chat ID: {chat_id})')
    # except IntegrityError:
    #     # Manejar el caso donde el chat_id ya existe (si es relevante para tu aplicación)
    #     print(f'El chat_id {chat_id} ya está registrado en la base de datos.')
    except Exception as e:
        logging.error(f'Error al guardar datos de usuario en la base de datos: {e}')


# Función para verificar si el chat_id ya está registrado en la base de datos
def verificar_registro(chat_id):
    try:
        return Usuario.select().where(Usuario.chat_id == chat_id).exists()
    except Exception as e:
        logging.error(f'Error al verificar el registro en la base de datos: {e}')
        