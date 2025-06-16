import pandas as pd
import matplotlib
matplotlib.use('Agg')  # ✅ Evita errores relacionados con tkinter
import matplotlib.pyplot as plt
import os
from telegram import Update
from telegram.ext import CallbackContext
from io import BytesIO

estado_usuarios = {}  # Para rastrear en qué paso está cada usuario


# Ruta correcta del archivo
ARCHIVO_EXCEL = r"C:\Users\PDESARROLLO2\OneDrive - MAS S.A.S\Escritorio\MaajiTelegrambot2025\ventas\ventas_excel.xlsx"

def mostrar_submenu_ventas(bot, message):
    mensaje = (
        "📊 🔧 Por favor, elige una de las siguientes alternativas disponibles:\n\n"
        "1️⃣ Ventas del mes\n"
        "2️⃣ Ventas de la semana\n"
        "3️⃣ Ventas del día\n"
        "4️⃣ Consultar ventas por mes y año\n\n"
        "Si deseas regresar al menú principal selecciona el comando /menu."
    )
    bot.send_message(chat_id=message.chat.id, text=mensaje)
def manejar_opcion_submenu_ventas(bot, message):
    opcion = message.text.strip()

    if opcion in ["1", "2", "3"]:
        periodos = {"1": "mes", "2": "semana", "3": "dia"}
        generar_venta_por_periodo(bot, message.chat.id, periodos[opcion])

    elif opcion == "4":
        bot.send_message(
            chat_id=message.chat.id,
            text="📅 ¿De qué *mes* quieres consultar las ventas? (Escribe solo el número del mes, por ejemplo: 1 para enero)",
            parse_mode="Markdown"
        )
        estado_usuarios[message.chat.id] = {"estado": "esperando_mes"}

    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="❌ Opción no válida. Escribe 'menu' para volver al menú principal."
        )


def manejar_mensajes_generales(bot, message):
    chat_id = message.chat.id
    texto = message.text.strip()

    # Verificamos si el usuario está en algún estado especial
    datos_usuario = estado_usuarios.get(chat_id)

    if datos_usuario and datos_usuario["estado"] == "esperando_mes":
        try:
            mes = int(texto)
            if mes < 1 or mes > 12:
                raise ValueError
            estado_usuarios[chat_id] = {"estado": "esperando_ano", "mes": mes}
            bot.send_message(chat_id=chat_id, text="📆 Ahora escribe el *año* que deseas consultar (por ejemplo 2024):", parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id=chat_id, text="❌ Por favor escribe un número de mes válido entre 1 y 12.")

    elif datos_usuario and datos_usuario["estado"] == "esperando_ano":
        try:
            ano = int(texto)
            mes = datos_usuario["mes"]
            del estado_usuarios[chat_id]
            mostrar_ventas_mes_ano(bot, chat_id, mes, ano)  # Esta la haremos en el siguiente paso
        except ValueError:
            bot.send_message(chat_id=chat_id, text="❌ Escribe un número de año válido (por ejemplo 2024).")


def mostrar_ventas_mes_ano(bot, chat_id, mes, ano):
    try:
        if not os.path.exists(ARCHIVO_EXCEL):
            bot.send_message(chat_id=chat_id, text="❌ No se encontró el archivo de ventas.")
            return

        df = pd.read_excel(ARCHIVO_EXCEL)
        df.columns = [col.strip().capitalize() for col in df.columns]

        if 'Fecha' not in df.columns or 'Total' not in df.columns:
            bot.send_message(chat_id=chat_id, text="❌ El archivo debe tener columnas 'Fecha' y 'Total'.")
            return

        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df_filtrado = df[(df['Fecha'].dt.month == mes) & (df['Fecha'].dt.year == ano)]

        if df_filtrado.empty:
            bot.send_message(chat_id=chat_id, text=f"📭 No hay ventas registradas para {mes:02d}/{ano}.")
            return

        total_ventas = df_filtrado['Total'].sum()
        df_por_dia = df_filtrado.groupby(df_filtrado['Fecha'].dt.date)['Total'].sum().reset_index()

        # 📈 Generar gráfico
        plt.figure(figsize=(10, 6))
        plt.bar(df_por_dia['Fecha'].astype(str), df_por_dia['Total'], color='teal')
        plt.title(f'📅 Ventas diarias - {mes:02d}/{ano}')
        plt.xlabel('Día')
        plt.ylabel('Total Ventas')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # 📷 Guardar imagen en memoria, no en disco
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        caption = f"📊 Total de ventas para {mes:02d}/{ano}: ${total_ventas:,.2f}\n"
        caption += f"Cada barra representa un día con ventas registradas."

        bot.send_photo(chat_id=chat_id, photo=buffer, caption=caption)

        bot.send_message(chat_id=chat_id, text="🏠 ¿Deseas volver al menú principal? Escribe *menu* para regresar.", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f"❌ Error al generar el gráfico: {e}")
        
def generar_venta_por_periodo(bot, chat_id, periodo):
    try:
        if not os.path.exists(ARCHIVO_EXCEL):
            bot.send_message(chat_id=chat_id, text="❌ No se encontró el archivo de ventas.")
            return

        df = pd.read_excel(ARCHIVO_EXCEL)
        df.columns = [col.strip().capitalize() for col in df.columns]

        if 'Fecha' not in df.columns or 'Total' not in df.columns:
            bot.send_message(chat_id=chat_id, text="❌ El archivo debe tener columnas 'Fecha' y 'Total'.")
            return

        df['Fecha'] = pd.to_datetime(df['Fecha'])

        if periodo == 'mes':
            df['Periodo'] = df['Fecha'].dt.to_period('M')
        elif periodo == 'semana':
            df['Periodo'] = df['Fecha'].dt.to_period('W')
        elif periodo == 'dia':
            df['Periodo'] = df['Fecha'].dt.date

        resumen = df.groupby('Periodo')['Total'].sum().reset_index()

        plt.figure(figsize=(10, 6))
        plt.bar(resumen['Periodo'].astype(str), resumen['Total'], color='skyblue')
        plt.title(f'📈 Ventas por {periodo.capitalize()}')
        plt.xlabel(periodo.capitalize())
        plt.ylabel('Total Ventas')
        plt.xticks(rotation=45)
        plt.tight_layout()

        imagen_path = f'reporte_ventas_{periodo}.png'
        plt.savefig(imagen_path)
        plt.close()

        with open(imagen_path, 'rb') as img:
            bot.send_photo(chat_id=chat_id, photo=img, caption=f"✅ Gráfico de ventas por {periodo} generado con éxito.")

        bot.send_message(chat_id=chat_id, text="🏠 ¿Deseas volver al menú principal? Escribe *menu* para regresar.", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f"❌ Error al generar el reporte: {e}")







































# def generar_venta_por_periodo(bot, chat_id, periodo):
#     try:
#         if not os.path.exists(ARCHIVO_EXCEL):
#             bot.send_message(chat_id=chat_id, text="❌ No se encontró el archivo de ventas.")
#             return

#         df = pd.read_excel(ARCHIVO_EXCEL)
#         df.columns = [col.strip().capitalize() for col in df.columns]

#         if 'Fecha' not in df.columns or 'Total' not in df.columns:
#             bot.send_message(chat_id=chat_id, text="❌ El archivo debe tener columnas 'Fecha' y 'Total'.")
#             return

#         df['Fecha'] = pd.to_datetime(df['Fecha'])

#         if periodo == 'mes':
#             df['Periodo'] = df['Fecha'].dt.to_period('M')
#         elif periodo == 'semana':
#             df['Periodo'] = df['Fecha'].dt.to_period('W')
#         elif periodo == 'dia':
#             df['Periodo'] = df['Fecha'].dt.date

#         resumen = df.groupby('Periodo')['Total'].sum().reset_index()

#         plt.figure(figsize=(10, 6))
#         plt.bar(resumen['Periodo'].astype(str), resumen['Total'], color='skyblue')
#         plt.title(f'📈 Ventas por {periodo.capitalize()}')
#         plt.xlabel(periodo.capitalize())
#         plt.ylabel('Total Ventas')
#         plt.xticks(rotation=45)
#         plt.tight_layout()

#         imagen_path = f'reporte_ventas_{periodo}.png'
#         plt.savefig(imagen_path)
#         plt.close()

#         with open(imagen_path, 'rb') as img:
#             bot.send_photo(chat_id=chat_id, photo=img, caption=f"✅ Gráfico de ventas por {periodo} generado con éxito.")
        
#     except Exception as e:
#         bot.send_message(chat_id=chat_id, text=f"❌ Error al generar el reporte: {e}")





# import pandas as pd
# import matplotlib.pyplot as plt
# import os
# from telegram import Update
# from telegram.ext import CallbackContext

# # Ruta correcta del archivo
# ARCHIVO_EXCEL = r"C:\Users\PDESARROLLO2\OneDrive - MAS S.A.S\Escritorio\MaajiTelegrambot2025\ventas\ventas_excel.xlsx"

# def mostrar_submenu_ventas(bot, message):
#     mensaje = (
#         "📊 🔧 Por favor, elige una de las siguientes alternativas disponibles:\n\n"
#         "1️⃣ Venta mes\n"
#         "2️⃣ Venta semana\n"
#         "3️⃣ Venta día\n\n"
#         "Envía el número de la opción:"
#     )
#     bot.send_message(chat_id=message.chat.id, text=mensaje)

# def manejar_opcion_submenu_ventas(bot, message):
#     opcion = message.text.strip()
#     if opcion in ["1", "2", "3"]:
#         periodos = {"1": "mes", "2": "semana", "3": "dia"}
#         generar_venta_por_periodo(bot, message.chat.id, periodos[opcion])
#     else:
#         bot.send_message(chat_id=message.chat.id, text="❌ Opción no válida. Usa 1, 2 o 3.")

# def generar_venta_por_periodo(bot, chat_id, periodo):
#     try:
#         if not os.path.exists(ARCHIVO_EXCEL):
#             bot.send_message(chat_id=chat_id, text="❌ No se encontró el archivo de ventas.")
#             return

#         df = pd.read_excel(ARCHIVO_EXCEL)
#         df.columns = [col.strip().capitalize() for col in df.columns]

#         if 'Fecha' not in df.columns or 'Total' not in df.columns:
#             bot.send_message(chat_id=chat_id, text="❌ El archivo debe tener columnas 'Fecha' y 'Total'.")
#             return

#         df['Fecha'] = pd.to_datetime(df['Fecha'])

#         if periodo == 'mes':
#             df['Periodo'] = df['Fecha'].dt.to_period('M')
#         elif periodo == 'semana':
#             df['Periodo'] = df['Fecha'].dt.to_period('W')
#         elif periodo == 'dia':
#             df['Periodo'] = df['Fecha'].dt.date

#         resumen = df.groupby('Periodo')['Total'].sum().reset_index()

#         plt.figure(figsize=(10, 6))
#         plt.bar(resumen['Periodo'].astype(str), resumen['Total'], color='skyblue')
#         plt.title(f'📈 Ventas por {periodo.capitalize()}')
#         plt.xlabel(periodo.capitalize())
#         plt.ylabel('Total Ventas')
#         plt.xticks(rotation=45)
#         plt.tight_layout()

#         imagen_path = f'reporte_ventas_{periodo}.png'
#         plt.savefig(imagen_path)
#         plt.close()

#         with open(imagen_path, 'rb') as img:
#             bot.send_photo(chat_id=chat_id, photo=img, caption=f"✅ Gráfico de ventas por {periodo} generado con éxito.")
#     except Exception as e:
#         bot.send_message(chat_id=chat_id, text=f"❌ Error al generar el reporte: {e}")



# import pandas as pd
# import matplotlib.pyplot as plt
# import os

# # Guarda el estado del usuario en el submenú
# usuarios_en_submenu = {}

# def mostrar_submenu_ventas(bot, message):
#     chat_id = message.chat.id
#     usuarios_en_submenu[chat_id] = True  # Activamos que este usuario está en el submenú

#     mensaje = (
#         "📊 🔧 Por favor, elige una de las siguientes alternativas disponibles:\n\n"
#         "1️⃣ Venta mes\n"
#         "2️⃣ Venta semana\n"
#         "3️⃣ Venta día\n\n"
#         "Envía el número de la opción:"
#     )
#     bot.send_message(chat_id=chat_id, text=mensaje, parse_mode="Markdown")


# def manejar_opcion_submenu_ventas(bot, message):
#     chat_id = message.chat.id

#     # Si el usuario no está en el submenú, no procesamos
#     if chat_id not in usuarios_en_submenu:
#         return

#     opcion = message.text.strip()
#     if opcion == "1":
#         generar_venta_por_periodo(bot, chat_id, 'mes')
#     elif opcion == "2":
#         generar_venta_por_periodo(bot, chat_id, 'semana')
#     elif opcion == "3":
#         generar_venta_por_periodo(bot, chat_id, 'dia')
#     else:
#         bot.send_message(chat_id=chat_id, text="❌ Opción no válida. Usa 1, 2 o 3.")
#         return

#     usuarios_en_submenu.pop(chat_id)  # Eliminar usuario del submenú después de la respuesta


# def generar_venta_por_periodo(bot, chat_id, periodo: str):
#     try:
#         archivo_excel = r'C:\Users\PDESARROLLO2\OneDrive - MAS S.A.S\Escritorio\MaajiTelegrambot2025\ventas\ventas_excel.xlsx'

#         if not os.path.exists(archivo_excel):
#             bot.send_message(chat_id=chat_id, text="❌ No se encontró el archivo de ventas.")
#             return

#         df = pd.read_excel(archivo_excel)
#         df.columns = [col.strip().capitalize() for col in df.columns]

#         if 'Fecha' not in df.columns or 'Total' not in df.columns:
#             bot.send_message(chat_id=chat_id, text="❌ Columnas necesarias: 'Fecha' y 'Total'.")
#             return

#         df['Fecha'] = pd.to_datetime(df['Fecha'])

#         if periodo == 'mes':
#             df['Periodo'] = df['Fecha'].dt.to_period('M')
#         elif periodo == 'semana':
#             df['Periodo'] = df['Fecha'].dt.to_period('W')
#         elif periodo == 'dia':
#             df['Periodo'] = df['Fecha'].dt.date
#         else:
#             bot.send_message(chat_id=chat_id, text="❌ Periodo no válido.")
#             return

#         resumen = df.groupby('Periodo')['Total'].sum().reset_index()

#         plt.figure(figsize=(10, 6))
#         plt.bar(resumen['Periodo'].astype(str), resumen['Total'], color='salmon')
#         plt.title(f'Reporte de Ventas por {periodo.capitalize()}')
#         plt.xlabel(periodo.capitalize())
#         plt.ylabel('Total Ventas')
#         plt.xticks(rotation=45)
#         plt.tight_layout()
#         plt.grid(axis='y')

#         ruta_imagen = f'reporte_ventas_{periodo}.png'
#         plt.savefig(ruta_imagen)
#         plt.close()

#         with open(ruta_imagen, 'rb') as img:
#             bot.send_photo(chat_id=chat_id, photo=img,
#                            caption=f"📈 Ventas por {periodo} generadas con éxito.")

#     except Exception as e:
#         bot.send_message(chat_id=chat_id, text=f"❌ Error al generar el reporte: {e}")
#         print(f"[ERROR] {e}")
