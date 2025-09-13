from flask import Flask, render_template, request, jsonify, session, send_from_directory, redirect, url_for, flash
from flask_cors import CORS
import json
import os
import sys
import time
from datetime import datetime, timedelta
from functools import wraps
import requests
from pathlib import Path
import sqlite3
from collections import defaultdict

# Configurar rutas de búsqueda para Android
possible_paths = [
    "/storage/emulated/0/chipi-web-app",
    "/sdcard/chipi-web-app",
    str(Path(__file__).parent),
    os.getcwd()
]

# Buscar y establecer la ruta correcta
app_path = None
for path in possible_paths:
    if os.path.exists(path):
        app_path = path
        sys.path.insert(0, path)
        os.chdir(path)
        print(f"✓ Aplicación ejecutándose desde: {path}")
        break

if not app_path:
    print("⚠️ No se pudo encontrar el directorio de la aplicación")
    app_path = os.getcwd()

# Cargar variables de entorno
from dotenv import load_dotenv

env_loaded = False
possible_env_paths = [
    "/storage/emulated/0/chipi-web-app/.env",
    "/sdcard/chipi-web-app/.env", 
    str(Path(__file__).parent / ".env"),
    ".env"
]

for env_path in possible_env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✓ Variables de entorno cargadas desde: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    print("⚠️ No se encontró archivo .env. Usando valores por defecto.")

# Ahora importar después de configurar las rutas
from database import DatabaseManager

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Inicializar base de datos
db_manager = DatabaseManager()

# Sistema de aprendizaje adaptativo
class AdaptiveLearningSystem:
    def __init__(self, db_manager):
        self.db = db_manager
        self.user_preferences = defaultdict(dict)
        self.conversation_patterns = defaultdict(list)
    
    def load_user_data(self, user_id):
        """Cargar datos de preferencias del usuario"""
        try:
            # Cargar conversaciones recientes
            conversations = self.db.get_conversations(user_id, limit=50)
            for conv in conversations:
                self.analyze_conversation_pattern(conv['user_message'], conv['bot_response'])
            
            print(f"✓ Sistema de aprendizaje cargado para usuario {user_id}")
        except Exception as e:
            print(f"❌ Error cargando datos de aprendizaje: {e}")
    
    def analyze_conversation_pattern(self, user_message, bot_response):
        """Analizar patrones en las conversaciones"""
        message_lower = user_message.lower()
        
        # Detectar preferencias basadas en interacciones
        if any(word in message_lower for word in ['recordatorio', 'recordar', 'alarma']):
            self.user_preferences['prefers_reminders'] = True
        
        if any(word in message_lower for word in ['contraseña', 'clave', 'password']):
            self.user_preferences['uses_password_manager'] = True
        
        if any(word in message_lower for word in ['contacto', 'familiar', 'hijo', 'hija']):
            self.user_preferences['manages_contacts'] = True
    
    def get_personalized_response(self, user_message, user_id):
        """Generar respuesta personalizada basada en historial"""
        message_lower = user_message.lower()
        
        # Priorizar temas basados en preferencias
        if self.user_preferences.get('prefers_reminders') and any(word in message_lower for word in ['recordar', 'recordatorio']):
            return "¿Quieres que te ayude a crear un recordatorio? Dime qué necesitas recordar y a qué hora."
        
        if self.user_preferences.get('uses_password_manager') and any(word in message_lower for word in ['contraseña', 'clave']):
            return "Puedo ayudarte con tus contraseñas. ¿Quieres guardar una nueva o ver las que tienes guardadas?"
        
        return None

# Inicializar sistema de aprendizaje
learning_system = AdaptiveLearningSystem(db_manager)

# Decorador para verificar autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Si la petición es JSON/AJAX devolvemos 401 JSON, sino redirigimos al index/login
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Acceso no autorizado'}), 401
            return redirect(url_for('index'))
        
        # Cargar datos de aprendizaje al iniciar sesión (mantener comportamiento existente)
        if 'learning_loaded' not in session:
            try:
                learning_system.load_user_data(session['user_id'])
            except Exception as e:
                # no impedir acceso si falla carga de aprendizaje
                print(f"Warning loading learning data: {e}")
            session['learning_loaded'] = True
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()
    
    if not phone or not password:
        return jsonify({'error': 'Por favor completa todos los campos'}), 400
    
    user = db_manager.validate_user(phone, password)
    if user:
        session['user_id'] = user['id']
        session['user_phone'] = phone
        session['learning_loaded'] = False  # Resetear aprendizaje para cargar nuevo
        
        return jsonify({'message': 'Login exitoso', 'redirect': '/dashboard'})
    
    return jsonify({'error': 'Número o contraseña incorrectos'}), 401

@app.route('/recovery')
def recovery():
    return render_template('recovery.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    # Obtener datos del formulario (no JSON)
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # Validaciones
    if not all([phone, password, confirm_password]):
        flash('Por favor completa todos los campos', 'error')
        return render_template('register.html')
    
    if password != confirm_password:
        flash('Las contraseñas no coinciden', 'error')
        return render_template('register.html')
    
    if not (phone.isdigit() and len(phone) == 10 and phone.startswith('3')):
        flash('Número de teléfono inválido. Debe tener 10 dígitos y comenzar con 3.', 'error')
        return render_template('register.html')
    
    if len(password) < 6:
        flash('La contraseña debe tener al menos 6 caracteres', 'error')
        return render_template('register.html')
    
    if db_manager.user_exists(phone):
        flash('Este número ya está registrado', 'error')
        return render_template('register.html')
    
    if db_manager.create_user(phone, password):
        flash('Registro exitoso. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('index'))
    
    flash('Error al crear la cuenta', 'error')
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html')

# Ruta para obtener historial de chat con búsqueda
@app.route('/api/chat/history')
@login_required
def chat_history():
    limit = request.args.get('limit', 50, type=int)
    search_query = request.args.get('search', '')
    
    conversations = db_manager.get_conversations(session['user_id'], limit)
    
    # Filtrar por búsqueda si se proporciona
    if search_query:
        search_lower = search_query.lower()
        conversations = [
            conv for conv in conversations 
            if search_lower in conv['user_message'].lower() or search_lower in conv['bot_response'].lower()
        ]
    
    return jsonify({'conversations': conversations})

# Ruta para buscar en conversaciones
@app.route('/api/chat/search')
@login_required
def search_chat():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query de búsqueda requerida'}), 400
    
    results = db_manager.search_conversations(session['user_id'], query)
    return jsonify({'results': results, 'query': query})

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    user_message = request.json.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Mensaje vacío'}), 400
    
    # Obtener historial de conversación
    history = db_manager.get_conversations(session['user_id'], limit=10)
    
    # Procesar el mensaje con la IA
    response = process_message_with_ai(user_message, session['user_phone'], history)
    
    # Guardar en el historial de conversación
    db_manager.save_conversation(session['user_id'], user_message, response)
    
    # Aprender del patrón de conversación
    learning_system.analyze_conversation_pattern(user_message, response)
    
    return jsonify({'response': response})

@app.route('/passwords')
@login_required
def passwords_page():
    return render_template('passwords.html')

@app.route('/api/passwords', methods=['GET', 'POST'])
@login_required
def manage_passwords():
    if request.method == 'GET':
        passwords = db_manager.get_passwords(session['user_id'])
        return jsonify({'passwords': passwords})
    
    # POST - Guardar nueva contraseña
    data = request.get_json()
    service = data.get('service', '')
    password = data.get('password', '')
    
    if not service or not password:
        return jsonify({'error': 'Faltan datos'}), 400
    
    if db_manager.save_password(session['user_id'], service, password):
        return jsonify({'message': 'Contraseña guardada correctamente'})
    
    return jsonify({'error': 'Error al guardar la contraseña'}), 500

@app.route('/api/get-passwords', methods=['GET'])
@login_required
def get_passwords():
    passwords = db_manager.get_passwords(session['user_id'])
    return jsonify({'passwords': passwords})

@app.route('/reminders')
@login_required
def reminders_page():
    return render_template('reminders.html')

@app.route('/api/reminders', methods=['GET', 'POST'])
@login_required
def manage_reminders():
    if request.method == 'GET':
        reminders = db_manager.get_reminders(session['user_id'])
        return jsonify({'reminders': reminders})
    
    # POST - Crear nuevo recordatorio
    data = request.get_json()
    text = data.get('text', '')
    time = data.get('time', '')
    
    if not text or not time:
        return jsonify({'error': 'Faltan datos'}), 400
    
    if db_manager.create_reminder(session['user_id'], text, time):
        return jsonify({'message': 'Recordatorio creado correctamente'})
    
    return jsonify({'error': 'Error al crear el recordatorio'}), 500

@app.route('/api/get-reminders', methods=['GET'])
@login_required
def get_reminders():
    reminders = db_manager.get_reminders(session['user_id'])
    return jsonify({'reminders': reminders})

@app.route('/contacts')
@login_required
def contacts_page():
    return render_template('contacts.html')

@app.route('/api/contacts', methods=['GET', 'POST'])
@login_required
def manage_contacts():
    if request.method == 'GET':
        contacts = db_manager.get_contacts(session['user_id'])
        return jsonify({'contacts': contacts})
    
    # POST - Crear nuevo contacto
    data = request.get_json()
    name = data.get('name', '')
    phone = data.get('phone', '')
    relationship = data.get('relationship', '')
    
    if not name or not phone:
        return jsonify({'error': 'Faltan datos'}), 400
    
    if db_manager.save_contact(session['user_id'], name, phone, relationship):
        return jsonify({'message': 'Contacto guardado correctamente'})
    
    return jsonify({'error': 'Error al guardar el contacto'}), 500

@app.route('/api/get-contacts', methods=['GET'])
@login_required
def get_contacts():
    contacts = db_manager.get_contacts(session['user_id'])
    return jsonify({'contacts': contacts})

@app.route('/api/clear-chat', methods=['POST'])
@login_required
def clear_chat():
    # Limpiar historial de chat
    if db_manager.clear_conversations(session['user_id']):
        # Reiniciar sistema de aprendizaje
        learning_system.user_preferences.clear()
        learning_system.conversation_patterns.clear()
        
        return jsonify({'message': 'Chat limpiado correctamente'})
    return jsonify({'error': 'Error al limpiar el chat'}), 500

@app.route('/api/user/preferences')
@login_required
def get_user_preferences():
    """Obtener preferencias del usuario para debugging"""
    return jsonify({
        'preferences': dict(learning_system.user_preferences),
        'user_id': session['user_id']
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Servir archivos estáticos
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

def test_api_connection(api_key):
    """Testea la conexión con la API de OpenRouter"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'data' in data:
                    return True, "Conexión exitosa con OpenRouter"
                else:
                    return True, "Conexión exitosa (formato de respuesta inesperado)"
            except:
                return True, "Conexión exitosa (respuesta no JSON)"
        else:
            return False, f"Error en la API: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

def process_message_with_ai(message, user_phone, history=None):
    """Procesa el mensaje con la IA"""
    if history is None:
        history = []
    
    # Primero intentar respuesta personalizada del sistema de aprendizaje
    personalized_response = learning_system.get_personalized_response(message, session['user_id'])
    if personalized_response:
        return personalized_response
    
    # Obtener API key de las variables de entorno
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('CHIPI_API_KEY')
    
    # Verificar si la API key existe y es válida
    if not api_key or not api_key.startswith('sk-or-v1-'):
        return fallback_ai_response(message)
    
    # Testear la conexión primero
    connection_ok, connection_msg = test_api_connection(api_key)
    if not connection_ok:
        print(f"❌ Error de conexión: {connection_msg}")
        return fallback_ai_response(message)
    
    # Preparar mensajes para la API
    messages = [{
        "role": "system", 
        "content": "Eres Chipi, un asistente virtual amable y servicial para adultos mayores. Responde de forma clara, simple y directa."
    }]
    
    # Agregar historial de conversación
    for conv in history:
        messages.append({"role": "user", "content": conv['user_message']})
        messages.append({"role": "assistant", "content": conv['bot_response']})
    
    # Agregar mensaje actual
    messages.append({"role": "user", "content": message})
    
    try:
        # Preparar solicitud a la API
        data = {
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/chipi-ai/chipi-assistant",
            "X-Title": "Chipi IA Assistant"
        }
        
        # Intentar hasta 3 veces en caso de error de conexión
        for attempt in range(3):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    print(f"❌ Error API (intento {attempt + 1}): {response.status_code}")
                    if attempt < 2:
                        time.sleep(1)
                        continue
                    return fallback_ai_response(message)
                    
            except (requests.ConnectionError, requests.Timeout) as e:
                print(f"❌ Error de conexión (intento {attempt + 1}): {str(e)}")
                if attempt < 2:
                    time.sleep(2)
                    continue
                return fallback_ai_response(message)
                
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return fallback_ai_response(message)

def fallback_ai_response(message):
    """Respuesta de respaldo cuando la API falla"""
    # Respuestas inteligentes predefinidas
    responses = {
        'hola': '¡Hola! Soy Chipi, tu asistente virtual. ¿En qué puedo ayudarte hoy?',
        'cómo estás': 'Estoy muy bien, gracias por preguntar. ¿Y tú cómo estás?',
        'qué puedes hacer': 'Puedo ayudarte con muchas cosas: guardar contraseñas, crear recordatorios, responder tus preguntas y más. ¿Qué necesitas?',
        'abrir': '¡Claro! ¿Qué aplicación quieres abrir? WhatsApp, Facebook, Instagram...',
        'recordatorio': 'Dime qué quieres que te recuerde y a qué hora.',
        'contraseña': 'Para guardar contraseñas, dime: "Mi contraseña de [servicio] es [contraseña]"',
        'contacto': 'Para guardar contactos, dime: "Guarda a [nombre] con el número [teléfono]"',
        'gracias': '¡De nada! Estoy aquí para ayudarte siempre que me necesites.',
    }
    
    # Búsqueda inteligente de respuestas
    message_lower = message.lower()
    
    for key in responses:
        if key in message_lower:
            return responses[key]
    
    # Respuestas contextuales
    if any(palabra in message_lower for palabra in ['whatsapp', 'facebook', 'instagram', 'twitter']):
        return f"¡Perfecto! Abriendo la aplicación que mencionaste."
    
    if any(palabra in message_lower for palabra in ['hora', 'fecha', 'día']):
        return f"Son las {datetime.now().strftime('%H:%M')} del {datetime.now().strftime('%d/%m/%Y')}"
    
    # Respuesta por defecto
    return "Entendido. ¿En qué más puedo ayudarte? Puedo guardar contraseñas, crear recordatorios o responder tus preguntas."

if __name__ == '__main__':
    # Información de diagnóstico
    print("=" * 60)
    print("🤖 CHIPI IA - Iniciando servidor")
    print("=" * 60)
    print(f"📁 Directorio: {os.getcwd()}")
    print(f"🗄️ Base de datos: {db_manager.db_path}")
    
    # Verificar API key
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('CHIPI_API_KEY')
    if api_key and api_key.startswith('sk-or-v1-'):
        print("✅ API key encontrada")
        connection_ok, connection_msg = test_api_connection(api_key)
        if connection_ok:
            print("✅ Conexión API verificada")
        else:
            print(f"❌ Error en conexión API: {connection_msg}")
    else:
        print("⚠️ API key no configurada - Modo local activado")
    
    print("=" * 60)
    print("🌐 Servidor iniciado: http://127.0.0.1:8000")
    print("🔄 Para detener: Ctrl + C")
    print("=" * 60)
    
    # Crear directorios necesarios
    os.makedirs('data', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=8000)