import telebot
import google.generativeai as genai
import pandas as pd
import os
import time
import subprocess
import requests
import logging
from datetime import datetime
from openpyxl import load_workbook
from model import model
from data import guardar_datos_usuario,verificar_registro, usuarios
# from modelosdb import AnalisisSentimiento, Usuario
from Ejecuciones import EjecucionesBOT
from peewee import DoesNotExist
from dotenv import load_dotenv
from modelosdb import Usuario
from telebot import types
# from bot import bot, registrar_nombre
# from openai import OpenAI #DEEPSEEK IMPORTACIÓN
load_dotenv()

CORREOS_FILE = "C:/Users/PDESARROLLO2/OneDrive - MAS S.A.S/Escritorio/MaajiTelegrambot2025/Correos/Bot2025.xlsx"

#Variable para el bot
BOT = os.getenv('BOT_KEY')

#Variable del key de genia
IA = os.getenv('GENIA_KEY')



# Configuración del logging
logging.basicConfig(
    filename='bot_errors.log',  # Nombre del archivo de logs
    level=logging.ERROR,  # Nivel de logs
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del log
    datefmt='%Y-%m-%d %H:%M:%S'  # Formato de fecha y hora
)


# # Configurar el bot de Telegram
bot = telebot.TeleBot(BOT, parse_mode=None)
genai.configure(api_key=IA)

# Iniciar sesión de chat
chat_session = model.start_chat()

# Variable para controlar el estado de la IA
ia_activada = True

# usuarios_que_aceptaron = set()

# def enviar_terminos(message):
#     try:
#         # Crea botones inline
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(
#             telebot.types.InlineKeyboardButton("📄 Términos y condiciones", url="https://maaji.com.co/pages/terms-conditions"),
#             telebot.types.InlineKeyboardButton("✅ Aceptar", callback_data="aceptar_terminos"),
#             telebot.types.InlineKeyboardButton("❌ Rechazar", callback_data="rechazar_terminos")
#         )

#         # Envía el mensaje con los términos y condiciones
#         bot.send_message(
#             chat_id=message.chat.id,
#             text="¿Aceptas nuestros términos y condiciones? 😊",
#             reply_markup=markup
#         )
#     except Exception as e:
#         bot.reply_to(message, f"Error: {str(e)}")
#         logging.error(f"Error al enviar los términos y condiciones: {str(e)}")

# @bot.message_handler(func=lambda message: message.chat.id not in usuarios_que_aceptaron)
# def iniciar_con_terminos(message):
#     enviar_terminos(message)

# @bot.callback_query_handler(func=lambda call: call.data in ["aceptar_terminos", "rechazar_terminos"])
# def respuesta_terminos(call):
#     if call.data == "aceptar_terminos":
#         usuarios_que_aceptaron.add(call.message.chat.id)
#         bot.send_message(call.message.chat.id, "¡Gracias por aceptar nuestros términos y condiciones! 🎉")
#     else:
#         bot.send_message(call.message.chat.id, "Has rechazado los términos. No podrás continuar. ❌")

# # Ejecutar el bot
# bot.polling()


# Ruta de la carpeta donde se guardarán las imágenes
CARPETA_IMAGENES = r"C:\Users\PDESARROLLO2\OneDrive - MAS S.A.S\Escritorio\MaajiTelegrambot2025\imagenes"

# Crear la carpeta si no existe
if not os.path.exists(CARPETA_IMAGENES):
    os.makedirs(CARPETA_IMAGENES)

# Función para guardar la imagen
def guardar_imagen(message: types.Message):
    try:
        # Verificar si el mensaje contiene una imagen
        if message.photo:
            # Obtener la imagen enviada por el usuario
            file_id = message.photo[-1].file_id  # Obtener el file_id de la imagen en la mejor calidad
            file_info = bot.get_file(file_id)  # Obtener la información del archivo
            downloaded_file = bot.download_file(file_info.file_path)  # Descargar la imagen

            # Crear un nombre único para el archivo
            nombre_archivo = f"imagen_{message.from_user.id}_{message.date}.jpg"
            ruta_archivo = os.path.join(CARPETA_IMAGENES, nombre_archivo)

            # Guardar la imagen en la carpeta local
            with open(ruta_archivo, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Responder al usuario
            bot.reply_to(message, f"✅ Imagen guardada correctamente en: {ruta_archivo}")
        else:
            bot.reply_to(message, "❌ No se detectó una imagen. Por favor, envía una imagen.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error al guardar la imagen: {str(e)}")

@bot.message_handler(content_types=['photo'])
def recibir_imagen(message):
    guardar_imagen(message)




# Manejador para el comando /start
@bot.message_handler(commands=['start','menu'])
def send_start(message):
    try:
        
        chat_id = message.chat.id
        if verificar_registro(chat_id):
            try:            
                usuario = Usuario.get(Usuario.chat_id == chat_id)  
                bot.send_message(chat_id, f"🤖¡Hola de nuevo, {usuario.nombre} {usuario.apellido} del área {usuario.area}!")
            except Usuario.DoesNotExist:
                bot.send_message(chat_id, "No se pudo encontrar tu información en la base de datos.")
            #bot.send_message(chat_id, f"🤖¡Hola de nuevo, {Usuario.nombre}{Usuario.apellido} del área {Usuario.area}!")
            mostrar_menu(message)
        else:
            bot.send_message(chat_id, "🤖¡Hola! antes de continuar debes registrarte😉")
            bot.send_message(chat_id, "Ingresa tu nombre")
            bot.register_next_step_handler(message, registrar_nombre)
    except Exception as e:
        logging.error(f"Error en el comando /start: {str(e) }")
   
# Función para enviar el menú de funciones disponibles
def mostrar_menu(message):
    try:
        
        chat_id = message.chat.id
        comandos_otras = [
            "1. Opción 1: Ejecucion Area Tecnologia",
            "2. Opción 2: Bot de Amazón",
            "3. Cancelar Proceso\n\n",
            "4  Enviar Comprobante"
            "Recuerda que si usas el comando /menu o /start te permitirá regresar al menú!"
        ]
        message_text = "Selecciona tu área escribiendo el número correspondiente:\n" + "\n".join(comandos_otras)
        # respuesta = "Ejecuciones:\n" + "\n".join(comandos_otras)
        # bot.send_message(message.chat.id, respuesta)
        bot.send_message(chat_id, message_text)
        bot.register_next_step_handler(message, procesar_seleccion_menu)
    except Exception as e:
        logging.error(f"Error al mostrar el menú: {str(e)}")
    
# Funcion para procesar lo que el usuario seleccione segun el menu
def procesar_seleccion_menu(message):
    try:
        
        chat_id = message.chat.id
        
        # opciones = None
        if message.text == '1':
            # Si el usuario selecciona la opción 1
            EjecucionesBOT.opcion_1(bot,message)
        elif message.text == '2':
            # Si el usuario selecciona la opción 2
            EjecucionesBOT.opcion_2(bot,message)
        elif message.text == '3':
            bot.send_message(chat_id, "Por favor, envía la imagen que deseas guardar.")
            bot.register_next_step_handler(message, recibir_imagen)
        elif message.text == '4':
            # Si el usuario selecciona la opción 3
            EjecucionesBOT.cancelar_proceso(bot,message) #PROCESO
        else:
            # Si el usuario elige una opción no válida
            bot.send_message(chat_id, "Opción no válida. Por favor selecciona 1,2 o 3")
            mostrar_menu(message)
    except Exception as e:
        logging.error(f"Error al procesar la selección del menú: {str(e)}")  
        

# Función para registrar el nombre del usuario
def registrar_nombre(message):
    try:
        
        chat_id = message.chat.id
        nombre = message.text
        usuarios[chat_id] = {'nombre': nombre}
        bot.send_message(chat_id, f"¿Tu nombre es {nombre}?")
        bot.register_next_step_handler(message, confirmar_nombre)
    except Exception as e:
        logging.error(f"Error al registrar el nombre: {str(e)}")


# Función para confirmar el nombre del usuario
def confirmar_nombre(message):
    try:
        
        chat_id = message.chat.id
        confirmacion = message.text.lower()
        if confirmacion == 'si':
            bot.send_message(chat_id, "Perfecto.")
            bot.send_message(chat_id, "Ingresa tu apellido")
            bot.register_next_step_handler(message, registrar_apellido)
        elif confirmacion == 'no':
            bot.send_message(chat_id, "Vamos a empezar de nuevo.")
            usuarios.pop(chat_id, None)  # Elimina al usuario de la lista si existe
            send_start(message)  # Reinicia el proceso de registro
        else:
            bot.send_message(chat_id, "Por favor responda 'Si' o 'No'.")
            bot.register_next_step_handler(message, confirmar_nombre)
    except Exception as e:
        logging.error(f"Error al confirmar el nombre: {str(e)}")
        
# Función para registrar el apellido del usuario
def registrar_apellido(message):
    try:
        
        chat_id = message.chat.id
        apellido = message.text
        usuarios[chat_id]['apellido'] = apellido
        bot.send_message(chat_id, f"¿Tu apellido es {apellido}?")
        bot.register_next_step_handler(message, confirmar_apellido)
    except Exception as e:
        logging.error(f"Error al registrar el apellido: {str(e)}")
        

# Función para confirmar el apellido del usuario
def confirmar_apellido(message):
    try:
        
        chat_id = message.chat.id
        confirmacion = message.text.lower()
        if confirmacion == 'si':
            bot.send_message(chat_id, "Entendido.")
            bot.send_message(chat_id,'Ingresa tu correo')
            bot.register_next_step_handler(message, registrar_correo)
            #mostrar_opciones_area(chat_id)
        elif confirmacion == 'no':
            bot.send_message(chat_id, "Vamos a empezar de nuevo.")
            usuarios.pop(chat_id, None)  # Elimina al usuario de la lista si existe
            send_start(message)  # Reinicia el proceso de registro
        else:
            bot.send_message(chat_id, "Por favor responda 'Si' o 'No'.")
            bot.register_next_step_handler(message, confirmar_apellido)
    except Exception as e:
        logging.error(f"Error al confirmar el apellido: {str(e)}")
        

#Función para registrar el apellido del usuario

def registrar_correo(message):
    try:
        
        chat_id = message.chat.id
        correo = message.text.strip()
        # Inicializamos correos_validos en None para asegurarnos de que siempre tenga un valor    
        correos_validos = None
        
        if not os.path.exists(CORREOS_FILE): 
            print("No se encontro el archivo correos")  
            bot.send_message(chat_id,"No se encontro el archivo correos")
            return
        
        try:       
            df = pd.read_excel(CORREOS_FILE) #Verifica los datos del excel
            if 'correo' not in df.columns: #verifica la columna correo
                bot.send_message(chat_id, "El archivo no contiene la columna correo")
                usuarios.pop(chat_id, None) #
                send_start(message)  # Reinicia el proceso 
            correos_validos = df['correo'].tolist() #da la lista de correos validos
        except Exception as e:
            print(f"Error al leer el archivo de correos: {e}") #Saca el error
            
        if  correo not in correos_validos: #verifica si el correo esta en la lista 
            bot.send_message(chat_id, "Lo siento, pero tu correo no hace parte de la empresa")
            usuarios.pop(chat_id, None) #
            send_start(message)  # Reinicia el proceso
    
        
        


        # # Verificar si el correo ya existe en la base de datos
        for usuario in Usuario.select():
            if usuario.correo == correo:
                bot.send_message(chat_id, "⚠️ Este correo ya está registrado. No puedes usarlo nuevamente.")
                usuarios.pop(chat_id, None)
                send_start(message)  # Reinicia el proceso


        # Si no está duplicado, continúa con el flujo
        usuarios[chat_id]['correo'] = correo
        bot.send_message(chat_id, f"¿Tu correo es {correo}?")
        bot.register_next_step_handler(message, confirmar_correo)
    except Exception as e:
        logging.error(f"Error al registrar el correo: {str(e)}")

def confirmar_correo(message):
    try:
        
        chat_id = message.chat.id
        confirmacion = message.text.lower()
        if confirmacion == 'si':
            bot.send_message(chat_id, "Perfecto.")
            bot.send_message(chat_id, "Ingresa tú número de télefono")
            bot.register_next_step_handler(message, registrar_telefono)
        elif confirmacion == 'no':
            bot.send_message(chat_id, "Vamos a empezar de nuevo.")
            usuarios.pop(chat_id, None)  # Elimina al usuario de la lista si existe
            send_start(message)  # Reinicia el proceso de registro
        else:
            bot.send_message(chat_id, "Por favor responda 'Si' o 'No'.")
            bot.register_next_step_handler(message, confirmar_correo) 
    except Exception as e:
        logging.error(f"Error al confirmar el correo: {str(e)}")
            


#Funcion Registro de telefono 

def registrar_telefono (message):
    try:
        chat_id = message.chat.id
        telefono = message.text
        usuarios[chat_id]['telefono'] = telefono 
        bot.send_message(chat_id, f"¿Tu número es {telefono}?")
        bot.register_next_step_handler(message, confirmar_telefono)
    except Exception as e:
        logging.error(f"Error al registrar el telefono: {str(e)}")

#Confirmar Telefono
    
def confirmar_telefono(message):
    try:
        
        chat_id = message.chat.id
        confirmacion = message.text.lower()
        if confirmacion == 'si':
            bot.send_message(chat_id, "Listo")
            mostrar_opciones_area(chat_id)
        elif confirmacion == 'no':
            bot.send_message(chat_id, "Vamos a empezar de nuevo.")
            usuarios.pop(chat_id, None)  # Elimina al usuario de la lista si existe
            send_start(message)  # Reinicia el proceso de registro
        else:
            bot.send_message(chat_id, "Por favor responda 'Si' o 'No'.")
            bot.register_next_step_handler(message, confirmar_telefono)
    except Exception as e:
        logging.error(f"Error al confirmar el telefono: {str(e)}")
       

# Función para mostrar las opciones de área
def mostrar_opciones_area(chat_id):
    try:
        
        opciones = [
            "1. Equipo Dev",
            "2. Soluciones",
            "3. Infraestructura",
            "4. Produccion",
            "5. Cedi"
        ]
        message_text = "Selecciona tu área escribiendo el número correspondiente:\n" + "\n".join(opciones)
        bot.send_message(chat_id, message_text)
        bot.register_next_step_handler_by_chat_id(chat_id, process_area_step)
    except Exception as e:
        logging.error(f"Error al mostrar las opciones de área: {str(e)}")


# Función para procesar la selección del área
def process_area_step(message):
    try:
        
        chat_id = message.chat.id
        area = None
        if message.text == '1':
            area = "Equipo Dev"
        elif message.text == '2':
            area = "Soluciones"
        elif message.text == '3':
            area = "Infraestructura"
        elif message.text == '4':
            area = "Produccion"
        elif message.text == '5':
            area = "Cedi"
        else:
            bot.send_message(chat_id, "Por favor selecciona un número válido.")
            mostrar_opciones_area(chat_id)
            return
        
        usuarios[chat_id]['area'] = area
        message_text = (
            "Confirmación de registro:\n\n"
            f"Nombres: {usuarios[chat_id]['nombre']}\n"
            f"Apellidos: {usuarios[chat_id]['apellido']}\n"
            f"Correo: {usuarios[chat_id]['correo']}\n"
            f"Telefono: {usuarios[chat_id]['telefono']}\n"
            f"Area: {usuarios[chat_id]['area']}\n\n"
            "¿Son estos datos correctos?"
        )
        bot.send_message(chat_id, message_text)
        bot.register_next_step_handler(message, confirmar_registro)
    except Exception as e:
        logging.error(f"Error al procesar la selección del área: {str(e)}")
    
    
# Función para confirmar el registro
def confirmar_registro(message):
    try:
        chat_id = message.chat.id
        respuesta = message.text.strip().lower()
        if respuesta == 'si':
            bot.send_message(chat_id, f"¡Es un placer tenerte aquí! {usuarios[chat_id]['nombre']} {usuarios[chat_id]['apellido']}")
            guardar_datos_usuario(chat_id, usuarios[chat_id])
            mostrar_menu(message)
            bot.send_message(chat_id, "🤖¡Puedes preguntarle a la IA lo que desees!😉")
        elif respuesta == 'no':
            usuarios.pop(chat_id, None)  # Elimina al usuario de la lista si existe
            bot.send_message(chat_id, "Vamos a empezar de nuevo.")
            send_start(message)  # Reinicia el proceso de registro
        else:
            bot.send_message(chat_id, "Por favor, responda 'si' o 'no'.")
            bot.register_next_step_handler(message, confirmar_registro)
    except Exception as e:
        logging.error(f"Error al confirmar el registro: {str(e)}")

# Manejador para el comando /eliminar
@bot.message_handler(commands=['eliminar'])
def eliminar_registro(message):
    try:
        
        chat_id = message.chat.id
        # Verificar si existe el registro
        if verificar_registro(chat_id):
            bot.send_message(chat_id, "¿Estás seguro que deseas eliminar tu registro? Si/No \n\nDe ser así, si deseas volver a interactuar con el Bot debes registrarte de nuevo.")
            bot.register_next_step_handler(message, confirmar_eliminacion)
        else:
            bot.send_message(chat_id, "No tienes ningún registro que eliminar.")
            
    except Exception as e:
        logging.error(f"Error al eliminar el registro: {str(e)}")

# Función para confirmar la eliminación
def confirmar_eliminacion(message):
    try:
        chat_id = message.chat.id
        respuesta = message.text.strip().lower()
        if respuesta == 'si':
            try:
                # Eliminar el registro de la base de datos
                usuario = Usuario.get(Usuario.chat_id == chat_id)
                usuario.delete_instance()
                # Eliminar el registro de la memoria
                usuarios.pop(chat_id, None)
                bot.send_message(chat_id, "Se ha eliminado tu registro correctamente.")
                print(f"Se ha eliminado el registro del chat_id: {usuario.chat_id} con los datos de: {usuario.nombre} {usuario.apellido} del area de {usuario.area} de la BD.")
            except DoesNotExist:
                bot.send_message(chat_id, "No se pudo encontrar tu registro en la base de datos.")
        elif respuesta == 'no':
            bot.send_message(chat_id, "Eliminación cancelada, puedes seguir interactuando con el Bot")
        else:
            bot.send_message(chat_id, "Por favor, responde 'si' o 'no'.")
            bot.register_next_step_handler(message, confirmar_eliminacion)
    except Exception as e:
        logging.error(f"Error al confirmar la eliminación: {str(e)}")
        
# #Prueba #1

@bot.message_handler(commands=['terminos'])
def enviar_encuesta(message):
    try:
        
        preguntas = ["¿Te gusta este bot?", "¿Qué área prefieres?"]
        opciones = ["Sí", "No"], 
        for i, pregunta in enumerate(preguntas):
            bot.send_poll(chat_id=message.chat.id, question=pregunta, options=opciones[i], is_anonymous=False)
    except Exception as e:
        logging.error(f"Error al enviar la encuesta: {str(e)}")
        
# # Funcion para enviar una encuesta *FUNCIONAL*
@bot.message_handler(commands=['encuesta'])
def enviar_encuesta(message):
    try:
        
        # Define una pregunta y opciones de ejemplo
        pregunta = "¿Qué te parecio el bot? 😉"
        opciones = ["Excelente", "Muy bueno", "Bueno", "Regular", "Malo"]

        try:    
            # Envía la encuesta
            bot.send_poll(
                chat_id=message.chat.id,
                question=pregunta,
                options=opciones,
                is_anonymous=False  # Configura si la encuesta será anónima o no
            )
        except Exception as e:
            bot.send_message(message.chat.id, f"Hubo un error al enviar la encuesta: {e}")
    except Exception as e:
        logging.error(f"Error al enviar la calificación: {str(e)}")
    
       
#PRUEBA #2 funcional 
        
# @bot.message_handler(commands=['terminos'])
# def enviar_encuesta(message):
#     try:
#         # Define una pregunta y opciones de ejemplo
#         pregunta = "Aceptas nuestros terminos y condiciones? 😉" 
#         opciones = ["Sí", "No"]

#         try:    
#             # Envía la encuesta
#             bot.send_poll(
#                 chat_id=message.chat.id,
#                 question=pregunta,
#                 options=opciones,
#                 is_anonymous=False  # Configura si la encuesta será anónima o no
#             )
#         except Exception as e:
#             bot.send_message(message.chat.id, f"Hubo un error al enviar la encuesta: {e}")
#     except Exception as e:
#         logging.error(f"Error al enviar la calificación: {str(e)}")  

@bot.message_handler(commands=['condiciones'])
def enviar_terminos(message):
    try:
        # Crea botones inline
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📄 Términos y condiciones", url="https://maaji.com.co/pages/terms-conditions"),
            telebot.types.InlineKeyboardButton("✅ Aceptar", callback_data="aceptar_terminos"),
            telebot.types.InlineKeyboardButton("❌ Rechazar", callback_data="rechazar_terminos")
        )

        # Envía todo en un solo mensaje
        bot.send_message(
            chat_id=message.chat.id,
            text="¿Aceptas nuestros términos y condiciones? 😊",
            reply_markup=markup
        )
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")
        logging.error(f"Error al enviar los términos y condiciones: {str(e)}")
        
# #Función `guardar_analisis_sentimiento()

# def guardar_analisis_sentimiento(usuario, respuesta_texto, analisis_ia):
#     # Crear un nuevo modelo en tu base de datos para almacenar análisis
#     AnalisisSentimiento.create(
#         usuario=usuario,
#         respuesta=respuesta_texto,
#         sentimiento=extraer_sentimiento(analisis_ia.text),  # Función para parsear la respuesta de la IA
#         fecha=datetime.now()
#     )
    
# #Analiza el sentimiento del mensaje
# analisis = model.generate_content(f"Analiza el sentimiento de: {message.text}") 

# #Funcion Extracción Estructurada
# def extraer_sentimiento(texto_analisis):
#     # Ejemplo de texto_analisis: "El sentimiento es positivo con un 90% de confianza."
#     if "positivo" in texto_analisis.lower():
#         return "Positivo"
#     elif "negativo" in texto_analisis.lower():
#         return "Negativo"
#     else:
#         return "Neutral"
    
# #if pregunta_actual.tipo == "texto_libre":
#     try:
#         # Generar análisis
#         prompt = f"""
#         Analiza el sentimiento del siguiente texto corporativo y responde en JSON:
#         {message.text}

#         Formato requerido:
#         {{
#             "sentimiento": "Positivo|Neutral|Negativo",
#             "razones": ["lista", "de", "palabras_clave"]
#         }}
#         """
        
#         response = model.generate_content(prompt)
#         analisis_data = json.loads(response.text)
        
#         # Guardar en base de datos
#         AnalisisSentimiento.create(
#             usuario=usuario,
#             respuesta=message.text,
#             sentimiento=analisis_data["sentimiento"],
#             metadata=json.dumps(analisis_data)
#         )
        
#     except Exception as e:
#         logging.error(f"Error en análisis de sentimiento: {str(e)}")
#         bot.reply_to(message, "⚠️ Error al analizar la respuesta. Se guardó solo el texto.")
# #Base de datos
# class AnalisisSentimiento(BaseModel):
#     usuario = ForeignKeyField(Usuario)
#     respuesta = TextField()
#     sentimiento = CharField()  # Positivo/Neutral/Negativo
#     fecha = DateTimeField(default=datetime.now)
#     metadata = TextField(null=True)  # Para guardar raw de la IA si es necesario
        
        
# #Prueba pendiente por probar *NO FUNCIONAL*
# @bot.poll_answer_handler(commands=['prueba'])
# def handle_poll_answer(pollAnswer):
#     print(pollAnswer)

# #Prueba pendiente por probar *NO FUNCIONAL*
# @bot.poll_answer_handler(commands=['prueba'])
# def handle_poll_answer(pollAnswer):
#     print(pollAnswer



