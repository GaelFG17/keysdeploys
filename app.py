import os
import json
from flask import Flask, request, jsonify
import mediapipe as mp
import numpy as np
from flask_cors import CORS
from PIL import Image, ImageDraw
import io
import base64
import requests
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Permitir todas las solicitudes CORS
CORS(app)

# Función para autenticar con Google Drive usando credenciales de servicio
def authenticate_drive():
    credentials_json = os.getenv('GOOGLE_CREDENTIALS')
    if not credentials_json:
        raise Exception("Las credenciales de Google no están configuradas.")
    
    credentials_dict = json.loads(credentials_json)
    scope = ['https://www.googleapis.com/auth/drive.file']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    
    gauth = GoogleAuth()
    gauth.credentials = creds
    return GoogleDrive(gauth)

@app.route('/upload', methods=['POST'])
def detectar_Puntos_Faciales():
    drive = authenticate_drive()

    if 'file' not in request.files:
        return jsonify({'error': 'No se recibió correctamente la imagen'})

    archivo = request.files['file']
    if archivo.filename == '':
        return jsonify({'error': 'No se cargó ninguna imagen'})

    if archivo:
        # Guardar el archivo temporalmente en el servidor
        archivo.save(archivo.filename)

        # Subir la imagen a Google Drive
        file_drive = drive.CreateFile({'title': archivo.filename})
        file_drive.SetContentFile(archivo.filename)
        file_drive.Upload()

        # Eliminar el archivo localmente después de subirlo
        os.remove(archivo.filename)

        # Obtener el ID del archivo y construir la URL de descarga
        file_id = file_drive['id']
        image_url = f'https://drive.google.com/uc?id={file_id}'

        # Descargar la imagen desde Google Drive
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content)).convert('RGB')

        # Aquí va el procesamiento de la imagen con MediaPipe (detección de puntos faciales)
        # ...

        return jsonify({'image_link': image_url})

if __name__ == '__main__':
    app.run(debug=True)
