import telebot
import google.generativeai as genai
import pandas as pd
import os
import time
import subprocess
import requests
import logging
import ventas
from datetime import datetime
from openpyxl import load_workbook
from model import model
from data import guardar_datos_usuario,verificar_registro, usuarios
from tecnologia_process import *
from peewee import DoesNotExist
from modelosdb import Usuario
from telebot import types
from ventas import mostrar_submenu_ventas
from ventas import manejar_opcion_submenu_ventas




# Import Update and CallbackContext for type hinting in async handler
from telegram import Update
from telegram.ext import CallbackContext
 
CORREOS_FILE = "C:/Users/PDESARROLLO2/OneDrive - MAS S.A.S/Escritorio/MaajiTelegrambot2025/Correos/Bot2025.xlsx"
 
#Variable para el bot
BOT = '7441443568:AAGgPPelE3Sm7-lN6ZJFFW-7m12BYuMdPiE'
#Variable del key de genia
IA = 'AIzaSyCrjAcf2MtUmSMyhSzsBJ_o4ggO5aoyoV0'
 
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
 
# Manejador para el comando /start
@bot.message_handler(commands=['start','menu'])
def send_start(message):
    try:
       
        chat_id = message.chat.id
        if verificar_registro(chat_id):
            try:            
                usuario = Usuario.get(Usuario.chat_id == chat_id)  
                bot.send_message(chat_id, f"🤖¡Hola de nuevo, {usuario.nombre} {usuario.apellido} del área {usuario.area}! \n\n ¿Qué proceso desear realizar?  ")
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
   
# # Función para enviar el menú de funciones disponibles
def mostrar_menu(message):
    try:
        chat_id = message.chat.id
        comandos_otras = [
            "🖥️ 1. Proceso del Área de Tecnología", 
            "📋 2. Reporte de Ventas",
            "🚪 3. Salir del Bot"
           
        ]
        message_text = "📋 Elige una de las siguientes alternativas disponibles:\n\n" + "\n".join(comandos_otras)
        bot.send_message(chat_id, message_text)
        bot.register_next_step_handler(message, procesar_seleccion_menu)
    except Exception as e:
        logging.error(f"Error al mostrar el menú: {str(e)}")
 
 
def procesar_seleccion_menu(message):
    try:
        if message.text == '1':
            TecnologiaProcess.menu_tecnologia(bot, message)

        elif message.text == '2':
            ventas.mostrar_submenu_ventas(bot, message)

        elif message.text == '3':
            TecnologiaProcess.salir_del_bot(bot, message)

        else:
            bot.send_message(message.chat.id, "⚠️ Opción no válida")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        bot.send_message(message.chat.id, "❌ Error procesando tu solicitud")

   
# # Funcion para procesar lo que el usuario seleccione segun el menu
# def procesar_seleccion_menu(message):
#     try:
#         if message.text == '1':
#             TecnologiaProcess.menu_tecnologia(bot, message)
#         elif message.text == '2':
#            ventas.generar_reporte_ventas(bot, message)
           
#         elif message.text == '3':
#             TecnologiaProcess.salir_del_bot(bot, message)
#     except Exception as e:
#         logging.error(f"Error: {str(e)}")
 
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
            "5. Cedi",
            "6. BI"
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
        elif message.text == '6':
            area = "BI"
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
    
#     # funcion opcion graficos
# @bot.message_handler(func=lambda message: True)
# def manejar_mensajes(message):
#     if message.text == '2':
#         mostrar_submenu_ventas(bot, message)
#     else:
#         manejar_opcion_submenu_ventas(bot, message)

# @bot.message_handler(func=lambda message: True)
# def manejar_mensajes(message):
#     if message.text in ['1', '2', '3']:
#         manejar_opcion_submenu_ventas(bot, message)
#     elif message.text == 'menu':  # usa esto para abrir el menú
#         mostrar_submenu_ventas(bot, message)
#     else:
#         bot.send_message(message.chat.id, "❌ Opción no válida. Escribe 'menu' para ver las opciones.")

@bot.message_handler(func=lambda message: True)
def manejar_mensajes(message):
    if message.text.lower() == 'menu':
        mostrar_menu(message)  # ✅ Función ya existente
    elif message.text in ['1', '2', '3', '4']:  # 👈 Aceptamos también la opción 4
        manejar_opcion_submenu_ventas(bot, message)
    else:
        bot.send_message(message.chat.id, "❌ Opción no válida. Escribe 'menu' para volver al menú principal.")


 
 
 
 
 
 
 
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
# @bot.message_handler(commands=['terminos'])
# def enviar_encuesta(message):
#     try:
       
#         preguntas = ["¿Te gusta este bot?", "¿Qué área prefieres?"]
#         opciones = ["Sí", "No"],
#         for i, pregunta in enumerate(preguntas):
#             bot.send_poll(chat_id=message.chat.id, question=pregunta, options=opciones[i], is_anonymous=False)
#     except Exception as e:
#         logging.error(f"Error al enviar la encuesta: {str(e)}")
       
# # # Funcion para enviar una encuesta *FUNCIONAL*
# @bot.message_handler(commands=['encuesta'])
# def enviar_encuesta(message):
#     try:
       
#         # Define una pregunta y opciones de ejemplo
#         pregunta = "¿Qué te parecio el bot? 😉"
#         opciones = ["Excelente", "Muy bueno", "Bueno", "Regular", "Malo"]
 
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
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📄 Términos y condiciones", url="https://maaji.com.co/pages/terms-conditions"),
            telebot.types.InlineKeyboardButton("✅ Aceptar", callback_data="aceptar_terminos"),
            telebot.types.InlineKeyboardButton("❌ Rechazar", callback_data="rechazar_terminos")
        )
 
        bot.send_message(
            chat_id=message.chat.id,
            text="¿Aceptas nuestros términos y condiciones? 😊",
            reply_markup=markup
        )
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")
        logging.error(f"Error al enviar términos: {str(e)}")
 
# Manejador para aceptar términos
@bot.callback_query_handler(func=lambda call: call.data == 'aceptar_terminos')
def aceptar_terminos(call):
    try:
        # Editar el mensaje original para eliminar los botones
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="¡Gracias por aceptar los términos y condiciones! 😊\n\nAhora puedes disfrutar de la plataforma.",
            reply_markup=None
        )
       
        # Opcional: Guardar en base de datos que el usuario aceptó
        # guardar_aceptacion(call.from_user.id)
       
    except Exception as e:
        logging.error(f"Error al aceptar términos: {str(e)}")
 
# Manejador para rechazar términos
@bot.callback_query_handler(func=lambda call: call.data == 'rechazar_terminos')
def rechazar_terminos(call):
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=(
                "❌ *No puedes continuar sin aceptar los términos.*\n\n"
                "Por favor abstente de usar esta plataforma.\n\n"
            ),
            parse_mode="Markdown",
            reply_markup=None
        )
       
    except Exception as e:
        logging.error(f"Error al rechazar términos: {str(e)}")