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
from tecnologia_process import *
from os.path import join as urljoin
import sharepointmaaji as conexion_maaji
from bot import *
 
 
class InfraestructuraProcess:
    # Ruta de la carpeta donde se guardarán las imágenes
    CARPETA_IMAGENES = r"C:\Users\PDESARROLLO2\OneDrive - MAS S.A.S\Escritorio\MaajiTelegrambot2025\imagenes"
 
    folder_relative_finished_img = 'Activos/Imagenes'
 
    # Crear la carpeta si no existe
    if not os.path.exists(CARPETA_IMAGENES):
        os.makedirs(CARPETA_IMAGENES)
 
    _imagen_temporal = None  # Variable para almacenar la imagen temporalmente
           
    @staticmethod
    def guardar_imagen(bot, message):
        try:
            if message.photo:
                # Descargar imagen y guardar temporalmente
                file_id = message.photo[-1].file_id
                file_info = bot.get_file(file_id)
                InfraestructuraProcess._imagen_temporal = bot.download_file(file_info.file_path)
               
                # Pedir nombre personalizado
                msg = bot.reply_to(message, "📝 *Escribe el nombre para la imagen:*")
                bot.register_next_step_handler(msg, lambda m: InfraestructuraProcess._guardar_con_nombre(bot, m))
               
            else:
                bot.send_message(message.chat.id, "❌ Primero envía una imagen")
 
        except Exception as e:
            logging.error(f"Error en opcion_3: {e}")
            bot.send_message(message.chat.id, "❌ Error al procesar la imagen")
           
            #bot send message opcion del menu anterior para el regreso al menu
 
    @staticmethod
    def _guardar_con_nombre(bot, message):
        try:
            # Validación de usuario
            user_id = message.from_user.id
            if user_id not in usuarios:
                return bot.reply_to(message, "❌ Debes registrarte primero")
 
            # Validación de nombre
            nombre = message.text.strip()
            if not nombre:
                return bot.reply_to(message, "❌ El nombre no puede estar vacío")
 
            # Diccionario de meses en español
            MESES = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
 
            # Obtener fecha actual y componentes
            fecha_actual = datetime.now()
            año = fecha_actual.strftime("%Y")
            mes_numero = fecha_actual.month
            mes_nombre = MESES[mes_numero]
 
            # Generar nombre único
            timestamp = fecha_actual.strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{nombre}_{timestamp}.jpg"
 
            # Establecer conexión con SharePoint
            ctx = conexion_maaji.sharepoint_connection()
            if not ctx:
                logging.error("Conexión a SharePoint fallida")
                return bot.reply_to(message, "❌ Error conectando a SharePoint")
 
            # Estructura de carpetas
            sharepoint_path = f"{InfraestructuraProcess.folder_relative_finished_img}/{año}/{mes_nombre}"
            root_url = "/sites/Actasdeentrega/Documentos compartidos"
            # Conexión
            ctx = conexion_maaji.sharepoint_connection()
            if not ctx:
                return bot.reply_to(message, "❌ Error de autenticación")
 
            # Verificar permisos básicos
            try:
                web = ctx.web
                ctx.load(web)
                ctx.execute_query()
                print(f"Conectado al sitio: {web.title}")
            except Exception as perm_error:
                logging.error(f"Error de permisos: {str(perm_error)}")
                return bot.reply_to(message, "🔒 Sin permisos en el sitio")
 
            # Crear solo año y mes
            if not conexion_maaji.create_folder(ctx, sharepoint_path):
                return bot.reply_to(message, "❌ Error creando subcarpetas")

            full_path = f"{root_url}/{sharepoint_path}".replace("//", "/")
            
            #prueba de subir archivo
            try:
                target_folder = ctx.web.get_folder_by_server_relative_url(full_path)
                target_folder.upload_file(nombre_archivo, InfraestructuraProcess._imagen_temporal).execute_query()
                bot.send_message(message.chat.id, "✅ Archivo subido correctamente")
                bot.send_message(message.chat.id, "🔙 Volviendo al menú principal...")

                try:
                    mostrar_menu(message)
                except Exception as e:
                    logging.error(f"Error mostrando el menú: {str(e)}")

            except Exception as upload_error:
                logging.error(f"Error subiendo archivo: {str(upload_error)}")
                return bot.reply_to(message, "❌ Error al subir el archivo")

                        
            
            # Subir archivo
            # try:
            #     target_folder = ctx.web.get_folder_by_server_relative_url(full_path)
            #     target_folder.upload_file(nombre_archivo, InfraestructuraProcess._imagen_temporal).execute_query()
            #     bot.send_message(message.chat.id, "✅ Archivo subido correctamente")
            #     # bot.message(message.chat.id, "✅ Archivo subido correctamente")
            #     bot.message(message.chat.id, "🔙 Volviendo al menú principal...")
            #     # bot.message(message.chat.id, "🔙 Volviendo al menú principal...")
            #     mostrar_menu(message)   
            # except Exception as upload_error:
            #     logging.error(f"Error subiendo archivo: {str(upload_error)}")
            #     return bot.reply_to(message, "❌ Error al subir el archivo")
 
        except Exception as error:
            logging.error(f"Error crítico: {str(error)}")
            bot.reply_to(message, f"❌ Error del sistema: {str(error)}")