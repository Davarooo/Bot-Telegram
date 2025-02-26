# plantillas.py
import telebot
import logging
import subprocess
import requests
from modelosdb import Usuario
from peewee import DoesNotExist
 
class EjecucionesBOT:
    @staticmethod
    def opcion_1(bot, message):
        try:
            
            # Función que se llama cuando el usuario selecciona la opción 1
            bot.send_message(message.chat.id, "Has seleccionado la Opción 1. Por favor, elige una de las siguientes alternativas disponibles:")
        
            # Opciones disponibles en la opción 1
            opciones_opcion_1 = [
                "1. Opción A: Ejecución área Tech",
                "2. Opción B: Ejecución protocolos",
                "3. Cancelar Proceso"
            ]
            message_text = "\n".join(opciones_opcion_1)
            bot.send_message(message.chat.id, message_text)
            bot.register_next_step_handler(message, lambda msg: EjecucionesBOT.procesar_opcion_1(bot, msg))
        except Exception as e:
            logging.error(f"Error en EjecucionesBOT.opcion_1: {e}")

    @staticmethod
    def procesar_opcion_1(bot, message):
        try:
            
            # Lógica para procesar la selección dentro de la opción 1
            if message.text == '1':
                bot.send_message(message.chat.id,  "Ejecutando área Tecnología")
                EjecucionesBOT.ejecutar_funcion_a(bot, message)
            elif message.text == '2':
                bot.send_message(message.chat.id, "Ejecutando protocolos del área tecnologica.")
                EjecucionesBOT.ejecutar_funcion_b(bot, message)
            else:
                bot.send_message(message.chat.id, "Opción no válida. Por favor selecciona 1,2 o 3")
                bot.register_next_step_handler(message, lambda msg: EjecucionesBOT.procesar_opcion_1(bot, msg))
        except Exception as e:
            logging.error(f"Error en procesar_opcion_1: {e}")
            
            
 
    @staticmethod
    def ejecutar_funcion_a(bot, message): #
        try:   
        # Función A que se ejecuta al seleccionar la opción A de la opción 1
            bot.send_message(message.chat.id, "Areá tecnológica en proceso")
            try:
                subprocess.run(["python", "C:/Users/PDESARROLLO2/OneDrive - MAS S.A.S/Escritorio/prueba diego/main.py"])
                print("Archivo encontrado y ejecutado correctamente.")
                bot.send_message(message.chat.id, "Archivo python ejecutado correctamente.")
            except Exception as e:
                print(e)
        except Exception as e:
            logging.error(f"Error en EjecucionesBOT.ejecutar_funcion_a: {e}")
 
    @staticmethod
    def ejecutar_funcion_b(bot, message):
        try:
            
            # Función B que se ejecuta al seleccionar la opción B de la opción 1
            bot.send_message(message.chat.id, "Proceso en acción")
        except Exception as e:
            logging.error(f"Error en EjecucionesBOT.ejecutar_funcion_b: {e}")
 
    @staticmethod  
    def opcion_2(bot, message):
        try:
            
            # Función que se llama cuando el usuario selecciona la opción 2
            bot.send_message(message.chat.id, "Has seleccionado Opción 2. Elige una de las siguientes opciones:")
        
            # Opciones disponibles en la opción 2
            opciones_opcion_2 = [
                "1. Opción A: Ordenes de Amazon",
                "2. Opción B: Seguimiento de pedidos",
                "3. Cancelar Proceso"
            ]
            message_text = "\n".join(opciones_opcion_2)
            bot.send_message(message.chat.id, message_text)
            bot.register_next_step_handler(message, lambda msg: EjecucionesBOT.procesar_opcion_2(bot, msg))
        except Exception as e:
            logging.error(f"Error en EjecucionesBOT.opcion_2: {e}")
 
    @staticmethod
    def procesar_opcion_2(bot, message):
        try:
            
            # Lógica para procesar la selección dentro de la opción 2
            if message.text == '1':
                bot.send_message(message.chat.id, "Has elegido Opción A: Verificar inventario")
                EjecucionesBOT.ejecutar_funcion_a_2(bot, message)
            elif message.text == '2':
                bot.send_message(message.chat.id, "Has elegido Opción B: Seguimiento de Envíos")
                EjecucionesBOT.ejecutar_funcion_b_2(bot, message)
            else:
                bot.send_message(message.chat.id, "Opción no válida. Por favor selecciona 1,2 o 3")
                bot.register_next_step_handler(message, lambda msg: EjecucionesBOT.procesar_opcion_2(bot, msg))
        except Exception as e:
            logging.error(f"Error en procesar_opcion_2: {e}")
   
     
     #Función para los menus
    @staticmethod  
    def cancelar_proceso(bot, message):
        try:
            
            chat_id = message.chat.id
            bot.send_message(message.chat.id, "Has cancelado el proceso. Si deseas volver al menú, /menu o /start.")
            return chat_id
        except Exception as e:
            logging.error(f"Error en cancelar_proceso: {e}")
        
        
    @staticmethod
    def ejecutar_funcion_a_2(bot, message):
        try:
            # Función A que se ejecuta al seleccionar la opción A de la opción 2
            bot.send_message(message.chat.id, "Analizando disponibilidad en Amazon...")
        except Exception as e:
            logging.error(f"Error en EjecucionesBOT.ejecutar_funcion_a_2: {e}")
 
    @staticmethod
    def ejecutar_funcion_b_2(bot, message):
        try:
            # Función B que se ejecuta al seleccionar la opción B de la opción 2
            bot.send_message(message.chat.id, "Consultando estado de los paquetes...")
        except Exception as e:
            logging.error(f"Error en EjecucionesBOT.ejecutar_funcion_b_2: {e}")
 
