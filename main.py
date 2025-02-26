import telebot
import logging
from bot import bot,registrar_nombre
from model import chat_session
from data import verificar_registro
from modelosdb import Usuario



# Cargar usuarios al iniciar el bot
#cargar_usuarios()


# Función para manejar todos los mensajes entrantes
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        
        chat_id = message.chat.id
    
        if verificar_registro(chat_id):
            usuario = Usuario.get(Usuario.chat_id == chat_id)
            response = chat_session.send_message(message.text).text
            bot.send_message(chat_id,"🤖" + usuario.nombre + ", " + response)
        else:
            bot.send_message(chat_id, "🤖¡Hola! antes de continuar debes registrarte😉")
            bot.send_message(chat_id, "Ingrese sus nombres")
            bot.register_next_step_handler(message, registrar_nombre)
    except Exception as e:
        logging.error("Error al procesar el mensaje:")




# Inicia el bot para que esté siempre activo
print('En ejecución✅')
bot.infinity_polling()
print('Bot detenido correctamente✅') 