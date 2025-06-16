from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import pandas as pd
import os
# from dotenv import load_dotenv
# from .env import sp_site_url, sp_client_id, sp_client_secret
 
#  datos sensibles
site_url = 'https://maaji.sharepoint.com/sites/Actasdeentrega'
client_id = '5c4a2faf-fb05-4584-97cd-ac545b04f94f'
client_secret = 'NW82OFF+NGpEYnI5Zk9ySkVTYWp4ci5kWG5CVUFKVkVTZURUV2E4cw=='


# #datos sensibles
# site_url = os.getenv (sp_site_url)
# client_id = os.getenv (sp_client_id)        
# client_secret = os.getenv (sp_client_secret)

 
# Función de conexión a Sharepoint
def sharepoint_connection():
    client_credentials = ClientCredential(client_id, client_secret)
    ctx = ClientContext(site_url).with_credentials(client_credentials)
    web = ctx.web
    ctx.load(web)
    ctx.execute_query()
    print('Authenticated into SharePoint as:', web.properties['Title'])
    print('-' *100)
    return ctx
 
 
# Obtener detalles en la lectura de la carpeta
def folder_details(ctx, folder_relative_path_in_process):
    '''
    LECTURA DE ARCHIVOS EN LA CARPETA
    @PARAM: ctx = VARIABLE DE CONEXIÓN AL SHAREPOINT
    @PARAM: folder_relative_path = RUTA DE LA CARPETA DONDE SE QUIEREN LEER LOS ARCHIVOS
    '''
    folder = ctx.web.get_folder_by_server_relative_url(folder_relative_path_in_process)
    fold_names = []
    sub_folders = folder.files
    ctx.load(sub_folders)
    ctx.execute_query()
    for s_folder in sub_folders:
        fold_names.append(s_folder.properties['Name'])
    return fold_names
 
 
 
def create_folder(ctx, folder_path):
    """
    Crea carpetas anidadas dentro de 'Documentos compartidos' en el sitio 'Actasdeentrega'.
    """
    try:
        root_url = "/sites/Actasdeentrega/Documentos compartidos"
        root_folder = ctx.web.get_folder_by_server_relative_url(root_url)
        ctx.load(root_folder)
        ctx.execute_query()

        folders = folder_path.strip("/").split("/")
        current_folder = root_folder

        for folder_name in folders:
            sub_folders = current_folder.folders
            ctx.load(sub_folders)
            ctx.execute_query()

            existing = next((f for f in sub_folders if f.properties["Name"] == folder_name), None)

            if existing:
                current_folder = existing
            else:
                current_folder = current_folder.folders.add(folder_name)
                ctx.execute_query()

        print("✅ Carpetas creadas correctamente.")
        return True

    except Exception as e:
        print(f"❌ Error creación carpeta: {str(e)}")
        return False

 
 
 
 
 
# # sharepoint_functions.py
# def create_folder(ctx, full_folder_path):
#     """
#     Crea carpetas dentro de la biblioteca de documentos especificada
#     """
#     try:
#         # 1. Obtener la URL base del sitio
#         web = ctx.web
#         ctx.load(web, ["Url"])  # Cargar propiedad Url
#         ctx.execute_query()
       
#         # 2. Construir ruta relativa correctamente
#         site_relative_url = web.url.replace(ctx.base_url, "")  # Ej: "/sites/Actasdeentrega"
       
#         # 3. Obtener la carpeta raíz de documentos
#         library = ctx.web.lists.get_by_title("Documentos compartidos")  # Nombre exacto de tu biblioteca
#         ctx.load(library)
#         ctx.execute_query()
       
#         # 4. Construir ruta completa relativa
#         target_path = f"{site_relative_url}/Documentos compartidos/Activos/Imagenes"
       
#         # 5. Crear solo año y mes
#         folder = library.root_folder.folders.add(target_path).execute_query()
       
#         return True
 
#     except Exception as e:
#         error_message = str(e)
#         if "already exists" in error_message:
#             return True
#         print(f"Error creación carpeta: {error_message}")
#         return False
   
def upload_to_sharepoint(ctx, file_name, file_bytes, folder_path):
    """
    Sube archivos a SharePoint desde memoria
    """
    try:
        target_folder = ctx.web.get_folder_by_server_relative_url(folder_path)
        target_folder.upload_file(file_name, file_bytes).execute_query()
        return True
    except Exception as e:
        print(f"Error subiendo archivo: {str(e)}")
        return False