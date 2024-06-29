import os
import json
import base64
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase

# Configuración de Pyrebase
config = {
    "apiKey": "AIzaSyD_jo9XSsYzxbpWFvM87-UoECH-zCZULYY",
    "authDomain": "bag-cffca.firebaseapp.com",
    "databaseURL": "",  # Agrega tu URL de base de datos si la tienes
    "projectId": "bag-cffca",
    "storageBucket": "bag-cffca.appspot.com",
    "messagingSenderId": "6693922801",
    "appId": "1:6693922801:web:cc90427d0f76d6cb80c650",
    "measurementId": ""  # Agrega tu Measurement ID si lo tienes
}

firebase = pyrebase.initialize_app(config)
auth_pyrebase = firebase.auth()

# Inicializar la app Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max size

# Configurar Firebase Admin SDK
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, uid):
        self.id = uid

@login_manager.user_loader
def load_user(user_id):
    try:
        user_record = auth.get_user(user_id)
        return User(uid=user_id)
    except:
        return None

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth_pyrebase.sign_in_with_email_and_password(email, password)
            user_id = user['localId']
            login_user(User(uid=user_id))
            return redirect('/')
        except Exception as e:
            print(e)
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth_pyrebase.create_user_with_email_and_password(email, password)
            user_id = user['localId']
            login_user(User(uid=user_id))
            return redirect('/')
        except Exception as e:
            print(e)
            return 'Error creating account'
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/estimate', methods=['POST'])
@login_required
def estimate():
    data = request.json
    image_data = data['image'].split(',')[1]
    num_scales = int(data.get('num_scales', 0))

    # Guardar la imagen temporalmente
    image_filename = secure_filename(f'image_{num_scales}.png')
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    with open(image_path, 'wb') as image_file:
        image_file.write(base64.b64decode(image_data))

    # Procesar la imagen
    image_processing_response = requests.post(
        'http://localhost:5001/process_image',
        json={'image_path': image_path}
    )
    if image_processing_response.status_code != 200:
        return jsonify({'error': 'Error al procesar la imagen'}), 500

    analysis = image_processing_response.json()
    print("Azure Vision Analysis:", json.dumps(analysis, indent=4))  # Imprimir datos devueltos por Azure Vision

    # Verificar si hay personas en la imagen
    detected_objects = analysis.get('objects', [])
    if any(obj['object'] == 'person' for obj in detected_objects):
        return jsonify({'error': 'No debe haber personas en la imagen, por favor intente nuevamente.'}), 400

    estimated_value, details = calculate_value(analysis, num_scales)

    return jsonify({'estimated_value': estimated_value, 'image_filename': image_filename, 'details': details, 'num_scales': num_scales})

def calculate_value(analysis, num_scales):
    base_value = 0
    details = {}

    detected_objects = analysis.get('objects', [])
    detected_tags = analysis.get('tags', [])

    high_value_items = ['computer', 'macbook', 'mac', 'laptop', 'cell phone', 'professional camera', 'mobile phone', 'telephone']
    low_value_items = ['mouse', 'keyboard', 'electronic device']

    # Revisar objetos detectados
    for obj in detected_objects:
        print(f"Detected object: {obj['object']}")  # Añadir logging de objetos detectados
        if obj['object'] in high_value_items:
            base_value += 50
            details[obj['object']] = details.get(obj['object'], 0) + 50
        elif obj['object'] in low_value_items:
            base_value += 20
            details[obj['object']] = details.get(obj['object'], 0) + 20

    # Revisar etiquetas detectadas
    for tag in detected_tags:
        print(f"Detected tag: {tag['name']}")  # Añadir logging de etiquetas detectadas
        if tag['name'] in high_value_items:
            base_value += 50
            details[tag['name']] = details.get(tag['name'], 0) + 50
        elif tag['name'] in low_value_items:
            base_value += 20
            details[tag['name']] = details.get(tag['name'], 0) + 20

    details["Número de escalas"] = num_scales * 100
    return base_value + num_scales * 100, details

@app.route('/generate_contract', methods=['POST'])
@login_required
def generate_contract():
    data = request.json
    estimated_value = int(data['value'])

    # Llamada al servicio de despliegue del contrato
    contract_response = requests.post(
        'http://localhost:5003/deploy_contract',
        json={'value': estimated_value}
    )

    if contract_response.status_code != 200:
        return jsonify({'error': 'Error al desplegar el contrato inteligente'}), 500

    return contract_response.json()

@app.route('/receipt')
@login_required
def receipt():
    txn_receipt_str = request.args.get('txn_receipt')
    payment_receipt_str = request.args.get('payment_receipt')

    txn_receipt = json.loads(txn_receipt_str)
    payment_receipt = json.loads(payment_receipt_str)

    return render_template('receipt.html', tx_receipt=txn_receipt, payment_receipt=payment_receipt)

@app.route('/result')
@login_required
def result():
    estimated_value = request.args.get('value')
    image_filename = request.args.get('image')
    details = json.loads(request.args.get('details'))
    num_scales = request.args.get('num_scales')
    image_url = url_for('static', filename=f'uploads/{image_filename}')
    return render_template('result.html', estimated_value=estimated_value, image_url=image_url, details=details, num_scales=num_scales)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
