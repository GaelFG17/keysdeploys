from flask import Flask, request, jsonify
import mediapipe as mp
import numpy as np
from flask_cors import CORS
from PIL import Image, ImageDraw
import io
import base64

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
        # Leer la imagen directamente del archivo usando Pillow
        image = Image.open(archivo).convert('RGB')
        
        # Convertir la imagen a un formato que MediaPipe pueda procesar
        image_np = np.array(image)

        # Inicializar MediaPipe para la detección de puntos clave faciales
        mp_face_mesh = mp.solutions.face_mesh

        # Verificar si la imagen se cargó correctamente
        if image_np is None:
            return jsonify({'error': 'Error al cargar la imagen'})

        # Iniciar la detección de puntos faciales con MediaPipe
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
            results = face_mesh.process(image_np)

            # Definir los índices de los puntos que deseas graficar
            puntos_deseados = [70, 55, 285, 300, 33, 468, 133, 362, 473, 263, 4, 185, 0, 306, 17]

            # Si se detectan puntos faciales
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    for idx, landmark in enumerate(face_landmarks.landmark):
                        # Verificar si el índice está en la lista de puntos deseados
                        if idx in puntos_deseados:
                            # Convertir las coordenadas normalizadas a píxeles
                            h, w, _ = image_np.shape
                            x = int(landmark.x * w)
                            y = int(landmark.y * h)

                            # Cambiar el punto ploteado por una "X"
                            size = 5  # Tamaño predefinido de la "X"
                            color = (255, 0, 0)  # Color de la "X", en este caso color rojo
                            thickness = 2  # Grosor de la "X"

                            # Dibujar la "X" en la imagen usando Pillow
                            draw = ImageDraw.Draw(image)
                            draw.line((x - size, y - size, x + size, y + size), fill=color, width=thickness)
                            draw.line((x - size, y + size, x + size, y - size), fill=color, width=thickness)

        # Convertir la imagen con puntos clave a base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return jsonify({'image': img_base64})

if __name__ == '__main__':
    app.run(debug=True)
