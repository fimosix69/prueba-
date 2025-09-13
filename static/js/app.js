// app.js - Sistema Cybernético de Chipi IA (Versión Corregida y Optimizada)

class ChipiApp {
    constructor() {
        this.isInitialized = false;
        this.currentTheme = 'cyber';
        this.accessibilitySettings = {
            fontSize: 'normal',
            highContrast: false,
            voiceEnabled: false,
            soundEffects: false
        };
        
        this.speech = null;
        this.observer = null;
        this.particleSystems = new Map();
        this.typewriterIntervals = new Map();
        
        // Bind de métodos para mantener el contexto
        this.handleGlobalKeydown = this.handleGlobalKeydown.bind(this);
        this.handleResize = this.handleResize.bind(this);
        this.handleSmoothScroll = this.handleSmoothScroll.bind(this);
        this.handleFormSubmit = this.handleFormSubmit.bind(this);
        this.handleInputFocus = this.handleInputFocus.bind(this);
        this.handleInputBlur = this.handleInputBlur.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        
        this.init();
    }

    async init() {
        try {
            await this.loadSettings();
            this.setupEventListeners();
            this.setupIntersectionObserver();
            await this.initializeAnimations();
            this.isInitialized = true;
            
            console.log('🚀 Chipi IA System Initialized');
        } catch (error) {
            console.error('Error initializing ChipiApp:', error);
            this.showNotification('Error al inicializar la aplicación', 'error');
        }
    }

    async loadSettings() {
        try {
            // Cargar configuración desde localStorage
            const savedSettings = localStorage.getItem('chipiSettings');
            if (savedSettings) {
                this.accessibilitySettings = {
                    ...this.accessibilitySettings,
                    ...JSON.parse(savedSettings)
                };
                this.applyAccessibilitySettings();
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    setupEventListeners() {
        // Solo event listeners esenciales
        document.addEventListener('keydown', this.handleGlobalKeydown);
        window.addEventListener('resize', this.debounce(this.handleResize, 250));
        
        // Smooth scroll para enlaces internos (solo si no es dispositivo táctil)
        if (!this.isTouchDevice()) {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', this.handleSmoothScroll);
            });
        }

        // Mejorar formularios
        this.enhanceForms();
    }

    setupIntersectionObserver() {
        try {
            // Observer para animaciones al hacer scroll
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('cyber-visible');
                        this.animateElement(entry.target);
                        // Dejar de observar después de la animación
                        this.observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });

            // Observar todos los elementos con la clase cyber-animate
            document.querySelectorAll('.cyber-animate').forEach(el => {
                this.observer.observe(el);
            });
        } catch (error) {
            console.error('Error setting up IntersectionObserver:', error);
        }
    }

    async initializeAnimations() {
        try {
            // Inicializar partículas en elementos específicos
            this.initParticles();
            
            // Efecto de escritura mecánica
            this.initTypewriterEffect();
        } catch (error) {
            console.error('Error initializing animations:', error);
        }
    }

    isTouchDevice() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    }

    initParticles() {
        // Solo inicializar partículas en dispositivos de escritorio con buena capacidad
        if (this.isTouchDevice() || !this.isPerformanceGood()) return;
        
        try {
            // Crear sistemas de partículas para elementos con data-particles
            document.querySelectorAll('[data-particles]').forEach(container => {
                const count = parseInt(container.dataset.particles) || 20;
                this.createParticleSystem(container, count);
            });
        } catch (error) {
            console.error('Error initializing particles:', error);
        }
    }

    isPerformanceGood() {
        // Verificar si el dispositivo tiene buen rendimiento
        const memory = navigator.deviceMemory || 4; // GB
        const cores = navigator.hardwareConcurrency || 4;
        
        return memory >= 4 && cores >= 4;
    }

    createParticleSystem(container, count) {
        try {
            const particles = [];
            
            for (let i = 0; i < count; i++) {
                const particle = document.createElement('div');
                particle.className = 'cyber-particle';
                particle.style.setProperty('--particle-size', `${Math.random() * 3 + 1}px`);
                particle.style.setProperty('--particle-delay', `${Math.random() * 2}s`);
                particle.style.setProperty('--particle-duration', `${Math.random() * 3 + 2}s`);
                
                // Posicionamiento aleatorio pero dentro del contenedor
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                
                container.appendChild(particle);
                particles.push(particle);
            }
            
            this.particleSystems.set(container, particles);
        } catch (error) {
            console.error('Error creating particle system:', error);
        }
    }

    cleanupParticles() {
        // Limpiar todos los sistemas de partículas
        this.particleSystems.forEach((particles, container) => {
            particles.forEach(particle => {
                if (particle.parentNode === container) {
                    container.removeChild(particle);
                }
            });
        });
        this.particleSystems.clear();
    }

    initTypewriterEffect() {
        try {
            document.querySelectorAll('[data-typewriter]').forEach(element => {
                const originalText = element.textContent;
                element.textContent = '';
                element.style.width = `${originalText.length}ch`;
                
                let i = 0;
                const intervalId = setInterval(() => {
                    if (i < originalText.length) {
                        element.textContent += originalText.charAt(i);
                        i++;
                    } else {
                        clearInterval(intervalId);
                        element.classList.add('typewriter-complete');
                        this.typewriterIntervals.delete(element);
                    }
                }, 100);
                
                this.typewriterIntervals.set(element, intervalId);
            });
        } catch (error) {
            console.error('Error initializing typewriter effect:', error);
        }
    }

    cleanupTypewriterEffects() {
        // Limpiar todos los intervalos de typewriter
        this.typewriterIntervals.forEach((intervalId, element) => {
            clearInterval(intervalId);
        });
        this.typewriterIntervals.clear();
    }

    handleGlobalKeydown(event) {
        try {
            // Atajos de teclado globales
            if (event.altKey) {
                switch(event.key) {
                    case '1':
                        event.preventDefault();
                        this.navigateTo('/dashboard');
                        break;
                    case '2':
                        event.preventDefault();
                        this.navigateTo('/chat');
                        break;
                    case '3':
                        event.preventDefault();
                        this.navigateTo('/passwords');
                        break;
                    case '0':
                        event.preventDefault();
                        const mainElement = document.querySelector('main');
                        if (mainElement) mainElement.focus();
                        break;
                }
            }

            // Modo accesibilidad: Ctrl + Alt + A
            if (event.ctrlKey && event.altKey && event.key === 'a') {
                event.preventDefault();
                this.toggleAccessibilityMenu();
            }
        } catch (error) {
            console.error('Error handling global keydown:', error);
        }
    }

    navigateTo(path) {
        // Navegar a una ruta específica
        if (window.location.pathname !== path) {
            window.location.href = path;
        }
    }

    handleSmoothScroll(event) {
        try {
            event.preventDefault();
            const targetId = event.currentTarget.getAttribute('href');
            if (!targetId || targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        } catch (error) {
            console.error('Error handling smooth scroll:', error);
        }
    }

    handleResize() {
        try {
            // Recalcular y ajustar elementos responsivos
            this.adjustResponsiveElements();
            
            // Recrear partículas si es necesario
            this.cleanupParticles();
            this.initParticles();
        } catch (error) {
            console.error('Error handling resize:', error);
        }
    }

    adjustResponsiveElements() {
        try {
            // Ajustar elementos según el tamaño de la pantalla
            const screenWidth = window.innerWidth;
            document.documentElement.style.setProperty('--viewport-width', `${screenWidth}px`);
        } catch (error) {
            console.error('Error adjusting responsive elements:', error);
        }
    }

    enhanceForms() {
        try {
            // Mejorar todos los formularios con validación visual
            document.querySelectorAll('form').forEach(form => {
                // Evitar múltiples event listeners
                if (form.hasAttribute('data-enhanced')) return;
                
                form.setAttribute('data-enhanced', 'true');
                form.addEventListener('submit', this.handleFormSubmit);
                
                form.querySelectorAll('input, textarea, select').forEach(input => {
                    input.addEventListener('focus', this.handleInputFocus);
                    input.addEventListener('blur', this.handleInputBlur);
                    input.addEventListener('input', this.handleInputChange);
                });
            });
        } catch (error) {
            console.error('Error enhancing forms:', error);
        }
    }

    handleFormSubmit(event) {
        try {
            const form = event.target;
            if (!this.validateForm(form)) {
                event.preventDefault();
                this.showFormError(form, 'Por favor, complete todos los campos requeridos correctamente.');
            }
        } catch (error) {
            console.error('Error handling form submit:', error);
            event.preventDefault();
        }
    }

    validateForm(form) {
        let isValid = true;
        
        try {
            form.querySelectorAll('[required]').forEach(input => {
                if (!this.validateInput(input)) {
                    isValid = false;
                }
            });
        } catch (error) {
            console.error('Error validating form:', error);
            isValid = false;
        }
        
        return isValid;
    }

    handleInputFocus(event) {
        event.target.parentElement.classList.add('cyber-input-focused');
    }

    handleInputBlur(event) {
        event.target.parentElement.classList.remove('cyber-input-focused');
        this.validateInput(event.target);
    }

    handleInputChange(event) {
        this.validateInput(event.target);
    }

    validateInput(input) {
        try {
            // Limpiar errores previos
            input.classList.remove('cyber-input-error');
            
            // Validar campo requerido
            if (input.hasAttribute('required') && !input.value.trim()) {
                input.classList.add('cyber-input-error');
                return false;
            }
            
            // Validaciones específicas por tipo
            if (input.type === 'email' && input.value.trim()) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value)) {
                    input.classList.add('cyber-input-error');
                    return false;
                }
            }
            
            if (input.type === 'tel' && input.value.trim()) {
                const phoneRegex = /^3\d{9}$/;
                if (!phoneRegex.test(input.value.replace(/\D/g, ''))) {
                    input.classList.add('cyber-input-error');
                    return false;
                }
            }
            
            if (input.type === 'password' && input.value.trim() && input.hasAttribute('minlength')) {
                const minLength = parseInt(input.getAttribute('minlength')) || 6;
                if (input.value.length < minLength) {
                    input.classList.add('cyber-input-error');
                    return false;
                }
            }
            
            return true;
        } catch (error) {
            console.error('Error validating input:', error);
            return false;
        }
    }

    showFormError(form, message) {
        this.showNotification(message, 'error');
        form.classList.add('cyber-form-error');
        
        setTimeout(() => {
            form.classList.remove('cyber-form-error');
        }, 5000);
    }

    applyAccessibilitySettings() {
        try {
            // Aplicar configuración de accesibilidad
            document.documentElement.setAttribute('data-font-size', this.accessibilitySettings.fontSize);
            document.documentElement.setAttribute('data-contrast', this.accessibilitySettings.highContrast ? 'high' : 'normal');
            
            if (this.accessibilitySettings.voiceEnabled) {
                this.setupVoiceFeedback();
            } else if (this.speech) {
                window.speechSynthesis.cancel();
            }
        } catch (error) {
            console.error('Error applying accessibility settings:', error);
        }
    }

    setupVoiceFeedback() {
        try {
            // Configurar feedback de voz
            if ('speechSynthesis' in window) {
                this.speech = new SpeechSynthesisUtterance();
                this.speech.lang = 'es-ES';
                this.speech.rate = 0.9;
                this.speech.pitch = 1;
                this.speech.volume = 0.8;
            }
        } catch (error) {
            console.error('Error setting up voice feedback:', error);
        }
    }

    speak(text) {
        try {
            if (this.accessibilitySettings.voiceEnabled && this.speech && text) {
                // Cancelar speech anterior
                window.speechSynthesis.cancel();
                
                this.speech.text = text;
                window.speechSynthesis.speak(this.speech);
            }
        } catch (error) {
            console.error('Error speaking text:', error);
        }
    }

    toggleAccessibilityMenu() {
        try {
            const menu = document.getElementById('accessibility-menu') || this.createAccessibilityMenu();
            menu.classList.toggle('active');
            
            // Hablar estado del menú
            if (menu.classList.contains('active')) {
                this.speak('Menú de accesibilidad abierto');
            } else {
                this.speak('Menú de accesibilidad cerrado');
            }
        } catch (error) {
            console.error('Error toggling accessibility menu:', error);
        }
    }

    createAccessibilityMenu() {
        try {
            const menu = document.createElement('div');
            menu.id = 'accessibility-menu';
            menu.className = 'cyber-accessibility-menu';
            menu.innerHTML = `
                <h3>Configuración de Accesibilidad</h3>
                <div class="menu-section">
                    <label>Tamaño de texto:</label>
                    <select id="font-size-select">
                        <option value="normal">Normal</option>
                        <option value="large">Grande</option>
                        <option value="x-large">Muy Grande</option>
                    </select>
                </div>
                <div class="menu-section">
                    <label>
                        <input type="checkbox" id="high-contrast-toggle">
                        Alto contraste
                    </label>
                </div>
                <div class="menu-section">
                    <label>
                        <input type="checkbox" id="voice-feedback-toggle">
                        Feedback de voz
                    </label>
                </div>
                <div class="menu-section">
                    <label>
                        <input type="checkbox" id="sound-effects-toggle">
                        Efectos de sonido
                    </label>
                </div>
                <button id="accessibility-close" class="cyber-button">Cerrar</button>
            `;
            
            document.body.appendChild(menu);
            this.setupAccessibilityMenuEvents(menu);
            return menu;
        } catch (error) {
            console.error('Error creating accessibility menu:', error);
            return null;
        }
    }

    setupAccessibilityMenuEvents(menu) {
        try {
            // Establecer valores actuales
            menu.querySelector('#font-size-select').value = this.accessibilitySettings.fontSize;
            menu.querySelector('#high-contrast-toggle').checked = this.accessibilitySettings.highContrast;
            menu.querySelector('#voice-feedback-toggle').checked = this.accessibilitySettings.voiceEnabled;
            menu.querySelector('#sound-effects-toggle').checked = this.accessibilitySettings.soundEffects;

            // Event listeners
            menu.querySelector('#font-size-select').addEventListener('change', (e) => {
                this.accessibilitySettings.fontSize = e.target.value;
                this.saveSettings();
                this.speak(`Tamaño de texto cambiado a ${e.target.value}`);
            });

            menu.querySelector('#high-contrast-toggle').addEventListener('change', (e) => {
                this.accessibilitySettings.highContrast = e.target.checked;
                this.saveSettings();
                this.speak(e.target.checked ? 'Alto contraste activado' : 'Alto contraste desactivado');
            });

            menu.querySelector('#voice-feedback-toggle').addEventListener('change', (e) => {
                this.accessibilitySettings.voiceEnabled = e.target.checked;
                this.saveSettings();
                this.speak(e.target.checked ? 'Feedback de voz activado' : 'Feedback de voz desactivado');
            });

            menu.querySelector('#sound-effects-toggle').addEventListener('change', (e) => {
                this.accessibilitySettings.soundEffects = e.target.checked;
                this.saveSettings();
                this.speak(e.target.checked ? 'Efectos de sonido activados' : 'Efectos de sonido desactivados');
            });

            menu.querySelector('#accessibility-close').addEventListener('click', () => {
                menu.classList.remove('active');
            });

            // Cerrar al hacer clic fuera del menú
            document.addEventListener('click', (e) => {
                if (menu.classList.contains('active') && !menu.contains(e.target)) {
                    menu.classList.remove('active');
                }
            });
        } catch (error) {
            console.error('Error setting up accessibility menu events:', error);
        }
    }

    async saveSettings() {
        try {
            localStorage.setItem('chipiSettings', JSON.stringify(this.accessibilitySettings));
            this.applyAccessibilitySettings();
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showNotification('Error al guardar la configuración', 'error');
        }
    }

    showNotification(message, type = 'info') {
        try {
            const notification = document.createElement('div');
            notification.className = `cyber-notification cyber-notification-${type}`;
            notification.setAttribute('role', 'alert');
            notification.setAttribute('aria-live', 'polite');
            notification.innerHTML = `
                <div class="notification-content">
                    <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                    <span>${message}</span>
                </div>
                <button class="notification-close" aria-label="Cerrar notificación">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            document.body.appendChild(notification);
            
            // Animación de entrada
            setTimeout(() => notification.classList.add('show'), 10);
            
            // Auto-eliminación después de 5 segundos
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 5000);
            
            // Cierre manual
            notification.querySelector('.notification-close').addEventListener('click', () => {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            });
            
            // Feedback de voz para notificaciones importantes
            if (this.accessibilitySettings.voiceEnabled && type !== 'info') {
                this.speak(message);
            }
        } catch (error) {
            console.error('Error showing notification:', error);
        }
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    animateElement(element) {
        try {
            const animation = element.dataset.animation || 'fadeInUp';
            element.style.animation = `${animation} 0.6s ease-out forwards`;
        } catch (error) {
            console.error('Error animating element:', error);
        }
    }

    // Método para limpiar recursos antes de destruir la instancia
    destroy() {
        // Limpiar event listeners
        document.removeEventListener('keydown', this.handleGlobalKeydown);
        window.removeEventListener('resize', this.handleResize);
        
        // Limpiar observador
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
        
        // Limpiar partículas
        this.cleanupParticles();
        
        // Limpiar typewriters
        this.cleanupTypewriterEffects();
        
        // Detener voz
        if (this.speech) {
            window.speechSynthesis.cancel();
        }
        
        this.isInitialized = false;
        console.log('🧹 Chipi IA System Cleaned Up');
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.chipiApp = new ChipiApp();
});

// Polyfills para funcionalidades modernas (solo si son necesarios)
if (!Element.prototype.closest) {
    Element.prototype.closest = function(s) {
        var el = this;
        if (!document.documentElement.contains(el)) return null;
        do {
            if (el.matches(s)) return el;
            el = el.parentElement || el.parentNode;
        } while (el !== null && el.nodeType === 1);
        return null;
    };
}

if (!Element.prototype.matches) {
    Element.prototype.matches = 
        Element.prototype.matchesSelector || 
        Element.prototype.mozMatchesSelector ||
        Element.prototype.msMatchesSelector || 
        Element.prototype.oMatchesSelector || 
        Element.prototype.webkitMatchesSelector ||
        function(s) {
            var matches = (this.document || this.ownerDocument).querySelectorAll(s),
                i = matches.length;
            while (--i >= 0 && matches.item(i) !== this) {}
            return i > -1;
        };
}

// Exportar para uso modular si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChipiApp;
}