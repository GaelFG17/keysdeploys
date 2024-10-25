from flask import Flask, request, jsonify, render_template
import os
import json
import mediapipe as mp
import numpy as np
from flask_cors import CORS
from PIL import Image, ImageDraw
import io
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configura las credenciales de Google Drive desde la variable de entorno
CLIENT_SECRET_JSON = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# ID de la carpeta donde deseas subir la imagen
FOLDER_ID = '1v8Xss5sKEEgyPHfEBtXYBTHtUevdrhjd'

@app.route('/')
def index():
    return render_template('index.html')

# Inicializar el servicio de Google Drive
def obtener_servicio_drive():
    creds = service_account.Credentials.from_service_account_info(
        json.loads(CLIENT_SECRET_JSON), scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

@app.route('/upload', methods=['POST'])
def detectar_Puntos_Faciales():
    # (Tu código existente para procesar la imagen)

if __name__ == '__main__':
    app.run(debug=True)
