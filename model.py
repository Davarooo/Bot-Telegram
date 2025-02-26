import google.generativeai as genai

# Crear la configuración del modelo generativo
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
 
# Crear el modelo generativo
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Iniciar la sesión de chat
chat_session = model.start_chat()