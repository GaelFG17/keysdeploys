from flask import Flask, request, jsonify, render_template
import cv2
import mediapipe as mp
import os
import base64
import numpy as np
from flask_cors import CORS

app = Flask(__name__)

# Permitir todas las solicitudes CORS
CORS(app)


@app.route('/upload', methods=['POST'])
def detectar_Puntos_Faciales():
    # Cargar la imagen
    if 'file' not in request.files:
        return jsonify({'error': 'No se recibió correctamente la imagen'})

    archivo = request.files['file']
    if archivo.filename == '':
        return jsonify({'error': 'No se cargó ninguna imagen'})

    if archivo:
        # Leer la imagen directamente del archivo sin guardarla
        image = cv2.imdecode(np.frombuffer(archivo.read(), np.uint8), cv2.IMREAD_COLOR)

        # Inicializar MediaPipe para la detección de puntos clave faciales
        mp_face_mesh = mp.solutions.face_mesh

        # Verificar si la imagen se cargó correctamente
        if image is None:
            return jsonify({'error': 'Error al cargar la imagen'})

        # Reescalar la imagen y convertir la imagen de BGR a RGB
        image = cv2.resize(image, (500, 500))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convertir la imagen a escala de grises para el procesamiento posterior
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Convertir la imagen gris a un formato BGR de nuevo para poder dibujar en color
        image_gray_bgr = cv2.cvtColor(image_gray, cv2.COLOR_GRAY2BGR)

        # Iniciar la detección de puntos faciales con MediaPipe
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
            results = face_mesh.process(image_rgb)

            # Definir los índices de los puntos que deseas graficar
            puntos_deseados = [70, 55, 285, 300, 33, 468, 133, 362, 473, 263, 4, 185, 0, 306, 17]

            # Si se detectan puntos faciales
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Dibujar puntos clave en la imagen original
                    for idx, landmark in enumerate(face_landmarks.landmark):
                        # Verificar si el índice está en la lista de puntos deseados
                        if idx in puntos_deseados:
                            # Convertir las coordenadas normalizadas a píxeles
                            h, w, _ = image.shape
                            x = int(landmark.x * w)
                            y = int(landmark.y * h)

                            # Cambiar el punto ploteado por una "X"
                            size = 5  # Tamaño predefinido de la "X"
                            color = (0, 0, 255)  # Color de la "X", en este caso color rojo
                            thickness = 2  # Grosor de la "X"

                            # Dibujar la "X"
                            cv2.line(image_gray_bgr, (x - size, y - size), (x + size, y + size), color, thickness)
                            cv2.line(image_gray_bgr, (x - size, y + size), (x + size, y - size), color, thickness)

        # Convertir la imagen con puntos clave a base64
        _, buffer = cv2.imencode('.png', image_gray_bgr)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'image': img_base64
        })

