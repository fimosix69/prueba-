import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Determinar las posibles rutas del archivo .env
possible_env_paths = [
    "/storage/emulated/0/chipi-web-app/.env",
    "/sdcard/chipi-web-app/.env", 
    str(Path(__file__).parent.parent / ".env"),
    str(Path(__file__).parent / ".env"),
    ".env"  # Directorio actual
]

# Cargar variables de entorno desde la primera ruta existente
env_loaded = False
env_vars = {}
for env_path in possible_env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✓ Variables de entorno cargadas desde: {env_path}")
        env_loaded = True
        
        # Leer variables manualmente para mejor control
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        break

if not env_loaded:
    print("⚠️ No se encontró archivo .env. Usando valores por defecto.")

class AppConfig:
    # Información de la aplicación
    APP_NAME = env_vars.get('APP_NAME', "Chipi IA")
    APP_VERSION = env_vars.get('APP_VERSION', "2.1.0")
    APP_DESCRIPTION = "Asistente Virtual para Adultos Mayores"

    # Configuración de seguridad
    SECRET_KEY = env_vars.get('SECRET_KEY', 'fallback-secret-key-' + os.urandom(24).hex())
    PASSWORD_MIN_LENGTH = 6
    SESSION_TIMEOUT = 3600
    MAX_LOGIN_ATTEMPTS = 5

    # Configuración de API - Llama 3.1 (Gratuito)
    API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    API_MODEL = "meta-llama/llama-3.1-8b-instruct"
    API_TIMEOUT = 30
    API_MAX_TOKENS = 1000
    API_TEMPERATURE = 0.7

    # Configuración de base de datos (usando rutas absolutas)
    DEFAULT_DB_PATH = "/storage/emulated/0/chipi-web-app/data/chipi.db"
    DATABASE_URI = env_vars.get('DATABASE_URI', DEFAULT_DB_PATH)

    # Configuración de accesibilidad
    MIN_FONT_SIZE = 16
    MAX_FONT_SIZE = 24

    # Obtener API key (con múltiples opciones de nombres)
    API_KEY = (
        env_vars.get('OPENROUTER_API_KEY') or 
        env_vars.get('CHIPI_API_KEY') or 
        env_vars.get('API_KEY') or 
        os.getenv('OPENROUTER_API_KEY') or 
        os.getenv('CHIPI_API_KEY') or 
        os.getenv('API_KEY')
    )

    @classmethod
    def get_api_key(cls):
        """Obtiene la API key de forma segura"""
        return cls.API_KEY

    @classmethod
    def is_api_configured(cls):
        """Verifica si la API está configurada correctamente"""
        return bool(cls.API_KEY and cls.API_KEY.startswith('sk-or-v1-'))

    @classmethod
    def ensure_directories(cls):
        """Asegura que existan los directorios necesarios"""
        # Crear directorio de datos si no existe
        data_dir = os.path.dirname(cls.DATABASE_URI)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            print(f"✓ Directorio creado: {data_dir}")

    @classmethod
    def test_api_connection(cls):
        """Testea la conexión con la API y devuelve resultado detallado"""
        if not cls.is_api_configured():
            return {"status": "error", "message": "API key no configurada"}
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {cls.API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Test de autenticación
            auth_response = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers=headers,
                timeout=10
            )
            
            if auth_response.status_code == 200:
                # Test de envío de mensaje
                test_data = {
                    "model": cls.API_MODEL,
                    "messages": [
                        {"role": "system", "content": "Eres un asistente útil."},
                        {"role": "user", "content": "Hola, responde con 'OK' si funciono."}
                    ],
                    "max_tokens": 10,
                    "temperature": 0.1
                }
                
                chat_response = requests.post(
                    cls.API_BASE_URL,
                    headers=headers,
                    json=test_data,
                    timeout=30
                )
                
                if chat_response.status_code == 200:
                    return {
                        "status": "success",
                        "message": "Conexión API exitosa",
                        "auth_test": auth_response.json(),
                        "chat_test": chat_response.json()
                    }
                else:
                    return {
                        "status": "error", 
                        "message": f"Error en chat: {chat_response.status_code}",
                        "details": chat_response.text
                    }
            else:
                return {
                    "status": "error", 
                    "message": f"Error de autenticación: {auth_response.status_code}",
                    "details": auth_response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error de conexión: {str(e)}"
            }

# Inicialización automática
AppConfig.ensure_directories()

# Mostrar estado de configuración al importar
print(f"🔧 Configuración cargada - API: {'✅' if AppConfig.is_api_configured() else '❌'}")
if AppConfig.is_api_configured():
    print(f"🔑 API Key: {AppConfig.API_KEY[:15]}...")