import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Azure Vision API credentials
AZURE_VISION_ENDPOINT = "https://securebag.cognitiveservices.azure.com/"
AZURE_VISION_SUBSCRIPTION_KEY = "736bb45404a2434b87a12cfb28c37e68"

# Verificar que las variables de entorno se cargaron correctamente
print(f"AZURE_VISION_ENDPOINT: {AZURE_VISION_ENDPOINT}")
print(f"AZURE_VISION_SUBSCRIPTION_KEY: {AZURE_VISION_SUBSCRIPTION_KEY}")

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    image_path = data['image_path']

    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': AZURE_VISION_SUBSCRIPTION_KEY
    }
    params = {
        'visualFeatures': 'Objects,Tags',
        'details': '',
        'language': 'en'
    }

    response = requests.post(
        f"{AZURE_VISION_ENDPOINT}/vision/v3.1/analyze",
        headers=headers,
        params=params,
        data=image_data
    )

    if response.status_code != 200:
        print("Error al procesar la imagen con Azure Vision:", response.text)  # Añadir logging del error
        return jsonify({'error': 'Error al procesar la imagen con Azure Vision'}), 500

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=5001)
