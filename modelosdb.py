from peewee import *
import logging
import time
# Conexión a la base de datos SQLite
db = SqliteDatabase('usuarios.db')

# Definición del modelo de usuario
class Usuario(Model):
    try:
        chat_id = IntegerField(unique=True)
        nombre = CharField()
        apellido = CharField()
        correo = CharField()
        telefono = CharField()
        area = CharField()
        

        class Meta:
            database = db  # Conectar este modelo a la base de datos 'usuarios.db'
    except Exception as e:
        logging.error(f"Error al crear la tabla: {e}")
# #tabla nueva #1
# class AnalisisSentimiento(BaseModel):
#     usuario = ForeignKeyField(Usuario)
#     respuesta = TextField()
#     sentimiento = CharField()  # Positivo/Neutral/Negativo
#     fecha = DateTimeField(default=datetime.now)
#     metadata = TextField(null=True)  # Para guardar raw de la IA si es necesario

# Crear la tabla si no existe
db.connect()
db.create_tables([Usuario])
