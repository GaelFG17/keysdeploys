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


# Inicializar el servicio de Google Drive
def obtener_servicio_drive():
    creds = service_account.Credentials.from_service_account_info(
        json.loads(CLIENT_SECRET_JSON), scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

@app.route('/upload', methods=['POST'])
def detectar_puntos_y_procesar_imagenes():
    if 'file' not in request.files:
        return jsonify({'error': 'No se recibió correctamente la imagen'})

    archivo = request.files['file']
    if archivo.filename == '':
        return jsonify({'error': 'No se cargó ninguna imagen'})

    # Leer la imagen original
    imagen_original = archivo.read()
    archivo.seek(0)
    image_np = np.array(Image.open(archivo).convert('RGB'))

    if image_np is None:
        return jsonify({'error': 'Error al cargar la imagen'})

    # Procesar la imagen original, brillo, giro horizontal y giro vertical
    imagen_con_puntos = Image.fromarray(image_np)
    imagen_brillo = ImageEnhance.Brightness(imagen_con_puntos).enhance(random.uniform(1.5, 2))
    imagen_girada_horizontal = imagen_con_puntos.transpose(Image.FLIP_LEFT_RIGHT)
    imagen_girada_vertical = imagen_con_puntos.transpose(Image.FLIP_TOP_BOTTOM)

    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
        results = face_mesh.process(image_np)
        puntos_deseados = [70, 55, 285, 300, 33, 468, 133, 362, 473, 263, 4, 185, 0, 306, 17]

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, landmark in enumerate(face_landmarks.landmark):
                    if idx in puntos_deseados:
                        h, w, _ = image_np.shape
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        size = 8
                        color = (255, 0, 0)
                        thickness = 4

                        # Dibujar en la imagen original con puntos
                        draw_puntos = ImageDraw.Draw(imagen_con_puntos)
                        draw_puntos.line((x - size, y - size, x + size, y + size), fill=color, width=thickness)
                        draw_puntos.line((x - size, y + size, x + size, y - size), fill=color, width=thickness)

                        # Dibujar en la imagen con brillo aumentado
                        draw_brillo = ImageDraw.Draw(imagen_brillo)
                        draw_brillo.line((x - size, y - size, x + size, y + size), fill=color, width=thickness)
                        draw_brillo.line((x - size, y + size, x + size, y - size), fill=color, width=thickness)

                        # Dibujar en la imagen girada horizontalmente
                        draw_girada_horizontal = ImageDraw.Draw(imagen_girada_horizontal)
                        x_girado_horizontal = w - x  # Coordenada X reflejada
                        draw_girada_horizontal.line((x_girado_horizontal - size, y - size, x_girado_horizontal + size, y + size), fill=color, width=thickness)
                        draw_girada_horizontal.line((x_girado_horizontal - size, y + size, x_girado_horizontal + size, y - size), fill=color, width=thickness)

                        # Dibujar en la imagen girada verticalmente
                        draw_girada_vertical = ImageDraw.Draw(imagen_girada_vertical)
                        y_girado_vertical = h - y  # Coordenada Y reflejada
                        draw_girada_vertical.line((x - size, y_girado_vertical - size, x + size, y_girado_vertical + size), fill=color, width=thickness)
                        draw_girada_vertical.line((x - size, y_girado_vertical + size, x + size, y_girado_vertical - size), fill=color, width=thickness)

    # Convertir las imágenes procesadas a base64
    def convertir_a_base64(imagen):
        buffered = io.BytesIO()
        imagen.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    img_data_puntos = convertir_a_base64(imagen_con_puntos)
    img_data_brillo = convertir_a_base64(imagen_brillo)
    img_data_girada_horizontal = convertir_a_base64(imagen_girada_horizontal)
    img_data_girada_vertical = convertir_a_base64(imagen_girada_vertical)

    # Subir la imagen original a Google Drive
    service = obtener_servicio_drive()
    archivo_drive = MediaIoBaseUpload(io.BytesIO(imagen_original), mimetype='image/png')
    archivo_metadata = {
        'name': archivo.filename,
        'mimeType': 'image/png',
        'parents': [FOLDER_ID]
    }
    archivo_drive_subido = service.files().create(body=archivo_metadata, media_body=archivo_drive).execute()

    return jsonify({
        'image_with_points_base64': img_data_puntos,
        'image_with_brightness_and_points_base64': img_data_brillo,
        'image_with_flip_horizontal_and_points_base64': img_data_girada_horizontal,
        'image_with_flip_vertical_and_points_base64': img_data_girada_vertical,
        'drive_id': archivo_drive_subido.get('id')
    })
