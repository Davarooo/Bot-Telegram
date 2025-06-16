import telebot
import logging
from telebot import types, TeleBot
import os
import subprocess
import requests
import datetime
from datetime import datetime
from modelosdb import Usuario
from peewee import DoesNotExist
from bot import usuarios
from infraestructura_process import *
 
 
 
class TecnologiaProcess: #FUNCIONAL        
    @staticmethod
    def menu_tecnologia(bot, message):
        try:
            opciones = [
                "🔧 Por favor, elige una de las siguientes alternativas disponibles:\n",    
                "🛠️ 1. Ejecución área de Soluciones",
                "🏗️ 2. Ejecución área de Infraestructura",
                "⚙️ 3. Ejecución área de Desarrollo",
                "🚪 4. Salir al Menú Principal"
            ]
            mensaje = "\n".join(opciones)
            bot.send_message(message.chat.id, mensaje)
            # Cambia "procesar_opciones_infra" por "procesar_areas" 👇
            bot.register_next_step_handler(message, lambda msg: TecnologiaProcess.procesar_areas(bot, msg))
        except Exception as e:
            logging.error(f"Error en menú de Tecnología: {str(e)}")
 
    @staticmethod
    def procesar_areas(bot, message):
        try:
            # Lógica para procesar la selección dentro de la opción 1
            if message.text == '1':
                bot.send_message(message.chat.id, "Esta opción no se encuentra disponible. Por favor, regresa al menú anterior.")
                TecnologiaProcess.volver_menu_anterior(bot, message)
            elif message.text == '2':
                bot.send_message(message.chat.id, "Ejecutando Infrastructura.")
                TecnologiaProcess.infra_menu_seleccion(bot, message)
            elif message.text == '3':
                bot.send_message(message.chat.id, "Esta opción no se encuentra disponible. Por favor, regresa al menú anterior.")
                TecnologiaProcess.volver_menu_anterior(bot, message)
            elif message.text == '4':
                # Mensaje de confirmación antes de regresar
                bot.send_message(message.chat.id, "Volviendo al menú anterior...")
                TecnologiaProcess.volver_al_menu_principal(bot, message)
            else:
                bot.send_message(message.chat.id,"Eleccion incorrecta, por favor seleccione una de las opciones disponibles")
                TecnologiaProcess.volver_menu_anterior(bot, message)
                # bot.register_next_step_handler(message, lambda msg: TecnologiaProcess.volver_al_menu_principal(bot, msg))
        except Exception as e:
            logging.error(f"Error en procesar_areas: {e}")
           
    #FUNCIONES
    @staticmethod
    def volver_al_menu_principal(bot, message):
        try:
            from bot import mostrar_menu  # Importa aquí, no al inicio del archivo
            bot.send_message(message.chat.id, "🔙 Volviendo al menú principal...")
            mostrar_menu(message)
        except Exception as e:
            logging.error(f"Error: {str(e)}")
 
    @staticmethod
    def volver_menu_anterior(bot, message):
        try:
            bot.send_message(message.chat.id, "🔙 Volviendo al menú anterior...")
            TecnologiaProcess.menu_tecnologia(bot, message)
        except Exception as e:
            logging.error(f"Error al regresar al menú: {e}")
 
    @staticmethod
    def infra_menu_seleccion(bot, message):
        try:
            opciones_menu_b = [
                "📋 Por favor, elige una de las siguientes alternativas disponibles:\n",
                "📤 1. Subir acta de entrega",
                "🔍 2. Volver al menú anterior"
            ]
            message_text = "\n".join(opciones_menu_b)
            bot.send_message(message.chat.id, message_text)
            bot.register_next_step_handler(message, lambda msg: TecnologiaProcess.procesar_opciones_infra(bot, msg)) #falta poner esta funcion
        except Exception as e:
            logging.error(f"Error en InfraestructuraProcess.menu_infra_seleccion: {e}")
   
    @staticmethod
    def procesar_opciones_infra(bot, message):
        try:
            # Procesar la selección del usuario en el menú de la opción B
            if message.text == '1':
                bot.send_message(message.chat.id, "Por favor, sube tu acta.")
                bot.register_next_step_handler(message, lambda msg: InfraestructuraProcess.guardar_imagen(bot, msg))
                # Aquí puedes implementar la lógica para manejar el archivo subido
            elif message.text == '2':
                bot.send_message(message.chat.id, "🔙 Volviendo al menú anterior...")
                TecnologiaProcess.menu_tecnologia(bot, message)
        except Exception as e:
            logging.error(f"Error en procesar_opcion_b: {e}")
           
           
    @staticmethod
    def salir_del_bot(bot, message):
        try:
            bot.send_message(message.chat.id, "✅ Has salido del menu principal, Si deseas realizar un proceso selecciona el comando /menu.")
        except Exception as e:
            logging.error(f"Error al salir: {str(e)}")
            
            
            
