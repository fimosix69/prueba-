import sqlite3
import hashlib
import os
import json
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path=None):
        # Determinar la ruta de la base de datos
        if db_path:
            self.db_path = db_path
        else:
            # Buscar en rutas posibles de Android
            possible_paths = [
                "/storage/emulated/0/chipi-web-app/data/chipi.db",
                "/sdcard/chipi-web-app/data/chipi.db",
                str(Path(__file__).parent / "data" / "chipi.db"),
                "data/chipi.db"
            ]
            
            for path in possible_paths:
                if os.path.exists(os.path.dirname(path)):
                    self.db_path = path
                    break
            else:
                # Usar una ruta por defecto
                self.db_path = "/storage/emulated/0/chipi-web-app/data/chipi.db"
        
        print(f"🗄️ Usando base de datos: {self.db_path}")
        self.init_db()
    
    def init_db(self):
        # Asegurar que el directorio existe
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        ''')
        
        # Tabla de conversaciones (MEJORADA con campo context)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de contraseñas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                service TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de recordatorios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                reminder_time TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de contactos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                relationship TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de preferencias de usuario (NUEVA para aprendizaje adaptativo)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_key),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, phone, password):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            cursor.execute(
                'INSERT INTO users (phone, password_hash) VALUES (?, ?)',
                (phone, password_hash)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return False
    
    def validate_user(self, phone, password):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            cursor.execute(
                'SELECT id, phone FROM users WHERE phone = ? AND password_hash = ?',
                (phone, password_hash)
            )
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {'id': user[0], 'phone': user[1]}
            return None
        except Exception as e:
            print(f"Error validando usuario: {e}")
            return None
    
    def user_exists(self, phone):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE phone = ?', (phone,))
            user = cursor.fetchone()
            conn.close()
            
            return user is not None
        except Exception as e:
            print(f"Error verificando usuario: {e}")
            return False
    
    def save_conversation(self, user_id, user_message, bot_response):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO conversations (user_id, user_message, bot_response) VALUES (?, ?, ?)',
                (user_id, user_message, bot_response)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error guardando conversación: {e}")
            return False
    
    # Función mejorada para guardar conversaciones con metadata
    def save_conversation_with_metadata(self, user_id, user_message, bot_response, context=None):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            context_json = json.dumps(context) if context else None
            
            cursor.execute(
                '''INSERT INTO conversations (user_id, user_message, bot_response, context) 
                   VALUES (?, ?, ?, ?)''',
                (user_id, user_message, bot_response, context_json)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error guardando conversación con metadata: {e}")
            return False

    def get_conversations(self, user_id, limit=10):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT user_message, bot_response, timestamp FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
                (user_id, limit)
            )
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'user_message': row[0],
                    'bot_response': row[1],
                    'timestamp': row[2]
                })
            
            conn.close()
            
            # Invertir para orden cronológico
            conversations.reverse()
            return conversations
        except Exception as e:
            print(f"Error obteniendo conversaciones: {e}")
            return []
    
    # Función para obtener historial completo con paginación
    def get_complete_conversation_history(self, user_id, limit=100, offset=0):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''SELECT user_message, bot_response, context, timestamp 
                   FROM conversations 
                   WHERE user_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ? OFFSET ?''',
                (user_id, limit, offset)
            )
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'user_message': row[0],
                    'bot_response': row[1],
                    'context': json.loads(row[2]) if row[2] else {},
                    'timestamp': row[3]
                })
            
            conn.close()
            return conversations
        except Exception as e:
            print(f"Error obteniendo historial completo: {e}")
            return []
    
    def search_conversation_history(self, user_id, search_term):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''SELECT user_message, bot_response, timestamp 
                   FROM conversations 
                   WHERE user_id = ? AND (user_message LIKE ? OR bot_response LIKE ?)
                   ORDER BY timestamp DESC 
                   LIMIT 50''',
                (user_id, f'%{search_term}%', f'%{search_term}%')
            )
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'user_message': row[0],
                    'bot_response': row[1],
                    'timestamp': row[2]
                })
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error buscando en historial: {e}")
            return []

    def clear_conversations(self, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error limpiando conversaciones: {e}")
            return False
    
    def save_password(self, user_id, service, password):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO passwords (user_id, service, password) VALUES (?, ?, ?)',
                (user_id, service, password)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error guardando contraseña: {e}")
            return False
    
    def get_passwords(self, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT service, password FROM passwords WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
            
            passwords = []
            for row in cursor.fetchall():
                passwords.append({
                    'service': row[0],
                    'password': row[1]
                })
            
            conn.close()
            return passwords
        except Exception as e:
            print(f"Error obteniendo contraseñas: {e}")
            return []
    
    def create_reminder(self, user_id, text, reminder_time):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO reminders (user_id, text, reminder_time) VALUES (?, ?, ?)',
                (user_id, text, reminder_time)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creando recordatorio: {e}")
            return False
    
    def get_reminders(self, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT id, text, reminder_time FROM reminders WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row[0],
                    'text': row[1],
                    'time': row[2]
                })
            
            conn.close()
            return reminders
        except Exception as e:
            print(f"Error obteniendo recordatorios: {e}")
            return []
    
    def save_contact(self, user_id, name, phone, relationship):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO contacts (user_id, name, phone, relationship) VALUES (?, ?, ?, ?)',
                (user_id, name, phone, relationship)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error guardando contacto: {e}")
            return False
    
    def get_contacts(self, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT id, name, phone, relationship FROM contacts WHERE user_id = ? ORDER BY name',
                (user_id,)
            )
            
            contacts = []
            for row in cursor.fetchall():
                contacts.append({
                    'id': row[0],
                    'name': row[1],
                    'phone': row[2],
                    'relationship': row[3] or ''
                })
            
            conn.close()
            return contacts
        except Exception as e:
            print(f"Error obteniendo contactos: {e}")
            return []
    
    # Funciones para el sistema de aprendizaje adaptativo
    def save_user_preference(self, user_id, key, value):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''INSERT OR REPLACE INTO user_preferences (user_id, preference_key, preference_value, updated_at)
                   VALUES (?, ?, ?, datetime('now'))''',
                (user_id, key, value)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error guardando preferencia: {e}")
            return False
    
    def get_user_preference(self, user_id, key, default=None):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT preference_value FROM user_preferences WHERE user_id = ? AND preference_key = ?',
                (user_id, key)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else default
        except Exception as e:
            print(f"Error obteniendo preferencia: {e}")
            return default
    
    def get_all_user_preferences(self, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT preference_key, preference_value FROM user_preferences WHERE user_id = ?',
                (user_id,)
            )
            
            preferences = {}
            for row in cursor.fetchall():
                preferences[row[0]] = row[1]
            
            conn.close()
            return preferences
        except Exception as e:
            print(f"Error obteniendo preferencias: {e}")
            return {}