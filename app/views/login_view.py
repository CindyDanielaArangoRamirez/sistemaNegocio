# app/views/login_view.py
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QApplication, QInputDialog # QDialog para herencia
)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap

from app.controllers.auth_controller import AuthController
from .register_view import RegisterView
# from .forgot_password_view import ForgotPasswordView # Necesitarás crear esta vista
# MainWindow no se importa aquí si main.py la maneja

class LoginView(QDialog): # Cambiado de nuevo a QDialog
    def __init__(self, parent=None): # QDialogs suelen tener un parent
        super().__init__(parent)
        self.store_name = "Ferretería YD"
        self.logo_file_name = "logo_ferreteria.png.png"
        self.user_logged_in_data = None # Para almacenar los datos del usuario tras un login exitoso
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Inicio de Sesión - {self.store_name}")

        # --- Estilo de Pantalla Completa y Contenedor Central ---
        # screen_geometry = QApplication.primaryScreen().geometry()
        # self.setGeometry(screen_geometry)
        # self.setStyleSheet("background-color: #2c3e50;")
        # Para un QDialog, es más común un tamaño fijo o que se ajuste al contenido,
        # en lugar de pantalla completa, a menos que sea un diseño muy específico.
        # Si quieres el estilo de contenedor blanco, aún puedes usar QFrame dentro del QDialog.
        self.setMinimumWidth(450) # Un ancho mínimo para el diálogo


        # Layout principal del QDialog
        dialog_main_layout = QVBoxLayout(self)
        # dialog_main_layout.setContentsMargins(0,0,0,0) # Si usas el Frame para todo el fondo

        self.central_container = QFrame(self) # Sigue siendo útil para el estilo del recuadro blanco
        self.central_container.setObjectName("authContainer")
        self.central_container.setStyleSheet("""
            QFrame#authContainer {
                background-color: white;
                border-radius: 15px; /* Menos redondeo para un diálogo más compacto */
                /* max-width: 400px; /* El diálogo ya controla el ancho */
                padding: 25px;
            }
        """)
        container_layout = QVBoxLayout(self.central_container)
        container_layout.setSpacing(15)
        container_layout.setAlignment(Qt.AlignCenter)
        
        dialog_main_layout.addWidget(self.central_container) # Añade el frame al layout del diálogo
        # --- Fin Estilo ---


        # --- INICIO: SECCIÓN DEL LOGO ---
        logo_display_label = QLabel() 
        logo_display_label.setAlignment(Qt.AlignCenter)
        try:
            # Estrategia de ruta: relativa al directorio de ESTE archivo (login_view.py)
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_root_dir = os.path.abspath(os.path.join(current_file_dir, "..", "..")) 
            logo_path = os.path.join(project_root_dir, "assets", self.logo_file_name)

            print(f"DEBUG (LoginView): current_file_dir: {current_file_dir}") # DEBUG
            print(f"DEBUG (LoginView): project_root_dir (calculado): {project_root_dir}") # DEBUG
            print(f"DEBUG (LoginView): Intentando cargar logo desde: {logo_path}") # DEBUG
            print(f"DEBUG (LoginView): os.path.exists para el logo: {os.path.exists(logo_path)}") # DEBUG
            
            assets_dir_path = os.path.join(project_root_dir, "assets") # DEBUG
            print(f"DEBUG (LoginView): os.path.exists para 'assets' en project_root: {os.path.exists(assets_dir_path)}") # DEBUG
            if os.path.exists(assets_dir_path): # DEBUG
                print(f"DEBUG (LoginView): Contenido de '{assets_dir_path}': {os.listdir(assets_dir_path)}") # DEBUG

            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                scaled_pixmap = pixmap.scaled(QSize(130, 130), Qt.KeepAspectRatio, Qt.SmoothTransformation) # Ajusta QSize(130,130) si es necesario
                logo_display_label.setPixmap(scaled_pixmap)
                logo_display_label.setStyleSheet("margin-bottom: 10px;") 
                container_layout.addWidget(logo_display_label) 
            else:
                print(f"Advertencia (LoginView): Logo no encontrado en {logo_path}")
        except Exception as e:
            print(f"Error al intentar cargar el logo en LoginView: {e}")
        # --- FIN: SECCIÓN DEL LOGO ---



        title_label = QLabel(self.store_name)
        title_label.setObjectName("authTitle")
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de usuario")
        self.username_input.setObjectName("authInput")
        container_layout.addWidget(QLabel("Usuario:"))
        container_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("authInput")
        container_layout.addWidget(QLabel("Contraseña:"))
        container_layout.addWidget(self.password_input)

        self.login_button = QPushButton("Ingresar")
        self.login_button.setObjectName("authButtonPrimary")
        self.login_button.clicked.connect(self.handle_login_attempt)
        container_layout.addWidget(self.login_button)

        links_layout = QHBoxLayout()
        links_layout.setContentsMargins(0, 10, 0, 0)

        self.forgot_password_button = QPushButton("¿Olvidaste tu contraseña?")
        self.forgot_password_button.setObjectName("authLinkButton")
        self.forgot_password_button.clicked.connect(self.handle_forgot_password_request)
        links_layout.addWidget(self.forgot_password_button)
        links_layout.addStretch()

        self.register_button = QPushButton("Registrarme")
        self.register_button.setObjectName("authLinkButton")
        self.register_button.clicked.connect(self.open_registration_dialog)
        links_layout.addWidget(self.register_button)
        container_layout.addLayout(links_layout)

        self.setLayout(dialog_main_layout) # Establecer el layout del QDialog

        # --- Aplicar estilos (si no usas un CSS global) ---
        if not self.styleSheet().count("authTitle"):
            self.setStyleSheet("background-color: #f0f0f0;") # Fondo para el QDialog si no es transparente
            title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #2c3e50; margin-bottom:10px;")
            for input_widget in [self.username_input, self.password_input]:
                input_widget.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 10pt;")
            self.login_button.setStyleSheet("""
                QPushButton#authButtonPrimary { padding: 8px; background-color: #3498db; color: white;
                                                border: none; border-radius: 4px; font-weight: bold; font-size: 10pt; }
                QPushButton#authButtonPrimary:hover { background-color: #2980b9; }
            """)
            for link_btn in [self.forgot_password_button, self.register_button]:
                link_btn.setStyleSheet("""
                    QPushButton#authLinkButton { background: transparent; color: #3498db; text-decoration: none;
                                                border: none; padding: 0; font-size: 9pt;}
                    QPushButton#authLinkButton:hover { text-decoration: underline; }
                """)


    def handle_login_attempt(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor, ingrese su nombre de usuario y contraseña.")
            return

        user_data = AuthController.login_user(username, password)

        if user_data:
            QMessageBox.information(self, "Inicio de Sesión Exitoso", f"¡Bienvenido de nuevo, {user_data['username']}!")
            self.user_logged_in_data = user_data # Guardar datos para que main.py los use
            self.accept() # Cierra el QDialog y devuelve QDialog.Accepted
        else:
            QMessageBox.warning(self, "Error de Inicio de Sesión", "Nombre de usuario o contraseña incorrectos.")
            self.password_input.clear()
            self.password_input.setFocus()

    def handle_forgot_password_request(self):
        email, ok = QInputDialog.getText(self, "Recuperar Contraseña", "Ingrese su correo electrónico registrado:")
        if ok and email:
            email = email.strip().lower()
            if "@" not in email or "." not in email.split('@')[-1]:
                QMessageBox.warning(self, "Email Inválido", "Formato de correo electrónico incorrecto.")
                return

            user_exists = AuthController.request_password_reset(email)
            if user_exists:
                QMessageBox.information(self, "Recuperación Iniciada",
                                        "Si el correo está registrado, recibirá instrucciones para restablecer su contraseña.")
            else:
                QMessageBox.warning(self, "Correo no Encontrado",
                                    "No se encontró una cuenta asociada a ese correo electrónico.")
        elif ok and not email:
             QMessageBox.warning(self, "Campo Vacío", "Por favor, ingrese un correo electrónico.")

    def open_registration_dialog(self):
        register_dialog = RegisterView(self)
        if register_dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Registro Completado",
                                    "¡Su cuenta ha sido creada exitosamente!\n"
                                    "Ahora puede iniciar sesión.")