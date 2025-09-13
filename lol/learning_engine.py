import json
import sqlite3
from datetime import datetime
from collections import defaultdict
import re

class LearningEngine:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.user_preferences = defaultdict(dict)
        self.conversation_patterns = defaultdict(list)
    
    def analyze_conversation_patterns(self, user_id):
        """Analiza patrones de conversación del usuario"""
        try:
            conversations = self.db_manager.get_complete_conversation_history(user_id, limit=500)
            
            # Analizar temas frecuentes
            topics = self._extract_topics(conversations)
            
            # Analizar horarios de uso
            usage_patterns = self._analyze_usage_patterns(conversations)
            
            # Aprender preferencias de comunicación
            communication_style = self._analyze_communication_style(conversations)
            
            user_profile = {
                'topics': topics,
                'usage_patterns': usage_patterns,
                'communication_style': communication_style,
                'last_analysis': datetime.now().isoformat()
            }
            
            self.user_preferences[user_id] = user_profile
            return user_profile
            
        except Exception as e:
            print(f"Error analizando patrones: {e}")
            return {}
    
    def _extract_topics(self, conversations):
        """Extrae temas frecuentes de las conversaciones"""
        topics = defaultdict(int)
        topic_keywords = {
            'medicina': ['medicina', 'pastilla', 'doctor', 'hospital', 'salud'],
            'familia': ['hijo', 'hija', 'nieto', 'familia', 'esposo', 'esposa'],
            'seguridad': ['contraseña', 'seguridad', 'hack', 'cuenta', 'correo'],
            'recordatorios': ['recordar', 'recordatorio', 'olvidar', 'memoria'],
            'tecnología': ['teléfono', 'app', 'aplicación', 'internet', 'wifi']
        }
        
        for conv in conversations:
            message = f"{conv['user_message']} {conv['bot_response']}".lower()
            
            for topic, keywords in topic_keywords.items():
                for keyword in keywords:
                    if keyword in message:
                        topics[topic] += 1
        
        return dict(topics)
    
    def _analyze_usage_patterns(self, conversations):
        """Analiza patrones de uso por hora del día"""
        hour_counts = defaultdict(int)
        
        for conv in conversations:
            if 'timestamp' in conv:
                try:
                    hour = datetime.strptime(conv['timestamp'], '%Y-%m-%d %H:%M:%S').hour
                    hour_counts[hour] += 1
                except:
                    continue
        
        return dict(hour_counts)
    
    def _analyze_communication_style(self, conversations):
        """Analiza el estilo de comunicación preferido del usuario"""
        style_metrics = {
            'formality_level': 0,
            'prefers_short_responses': 0,
            'prefers_examples': 0,
            'prefers_emotional_support': 0
        }
        
        for conv in conversations:
            user_msg = conv['user_message'].lower()
            bot_resp = conv['bot_response']
            
            # Medir formalidad
            if any(word in user_msg for word in ['por favor', 'gracias', 'quisiera']):
                style_metrics['formality_level'] += 1
            
            # Preferencia por respuestas cortas
            if len(bot_resp.split()) < 20:
                style_metrics['prefers_short_responses'] += 1
            
            # Preferencia por ejemplos
            if 'ejemplo' in user_msg or 'ejemplos' in user_msg:
                style_metrics['prefers_examples'] += 1
            
            # Preferencia por apoyo emocional
            if any(word in user_msg for word in ['triste', 'preocupado', 'ansioso', 'solo']):
                style_metrics['prefers_emotional_support'] += 1
        
        # Normalizar métricas
        total = len(conversations) or 1
        for key in style_metrics:
            style_metrics[key] = style_metrics[key] / total
        
        return style_metrics
    
    def get_personalized_response(self, user_id, message, context):
        """Genera una respuesta personalizada basada en el perfil del usuario"""
        profile = self.user_preferences.get(user_id, {})
        
        # Aplicar preferencias de estilo
        response_style = self._apply_communication_style(profile.get('communication_style', {}))
        
        # Añadir contexto relevante basado en historial
        contextual_info = self._get_contextual_info(user_id, message, profile)
        
        return {
            'response_style': response_style,
            'contextual_info': contextual_info,
            'personalization_level': len(profile) > 0
        }
    
    def _apply_communication_style(self, style_metrics):
        """Aplica el estilo de comunicación preferido"""
        style_rules = {}
        
        if style_metrics.get('prefers_short_responses', 0) > 0.6:
            style_rules['max_length'] = 100
        else:
            style_rules['max_length'] = 300
        
        if style_metrics.get('formality_level', 0) > 0.7:
            style_rules['tone'] = 'formal'
        else:
            style_rules['tone'] = 'amigable'
        
        if style_metrics.get('prefers_examples', 0) > 0.5:
            style_rules['include_examples'] = True
        else:
            style_rules['include_examples'] = False
        
        return style_rules
    
    def _get_contextual_info(self, user_id, current_message, profile):
        """Obtiene información contextual del historial"""
        contextual_info = {}
        
        # Buscar conversaciones relacionadas
        related_conversations = self.db_manager.search_conversation_history(
            user_id, self._extract_keywords(current_message)
        )
        
        if related_conversations:
            contextual_info['previous_topics'] = related_conversations[:3]
        
        # Sugerir temas basados en intereses
        topics = profile.get('topics', {})
        if topics:
            contextual_info['suggested_topics'] = sorted(
                topics.items(), key=lambda x: x[1], reverse=True
            )[:3]
        
        return contextual_info
    
    def _extract_keywords(self, message):
        """Extrae palabras clave para búsqueda"""
        stop_words = {'el', 'la', 'los', 'las', 'de', 'en', 'y', 'o', 'un', 'una', 'es', 'son'}
        words = re.findall(r'\b[a-záéíóúñ]+\b', message.lower())
        return ' '.join([word for word in words if word not in stop_words][:3])