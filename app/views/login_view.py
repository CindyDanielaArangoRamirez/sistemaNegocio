from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from app.controllers.auth_controller import AuthController
from app.views.register_view import RegisterView

class LoginView(QDialog):
    """Vista de inicio de sesión con formulario de login, recuperación de contraseña y registro"""
    
    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Inicio de Sesión - Ferretería")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Logo o título
        title = QLabel("Ferretería XYZ")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #2c3e50;
            qproperty-alignment: AlignCenter;
        """)
        
        # Formulario de login
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        
        self.login_btn = QPushButton("Ingresar")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        
        form_layout.addWidget(QLabel("Correo:"))
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(QLabel("Contraseña:"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)
        
        # Links inferiores
        links_layout = QHBoxLayout()
        links_layout.setContentsMargins(0, 10, 0, 0)
        
        self.forgot_btn = QPushButton("¿Olvidaste tu contraseña?")
        self.forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent; 
                color: #7f8c8d;
                text-decoration: underline;
                border: none;
                padding: 0;
            }
        """)
        self.forgot_btn.clicked.connect(self.handle_forgot_password)
        
        self.register_btn = QPushButton("Registrarme")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background: transparent; 
                color: #16a085;
                text-decoration: underline;
                border: none;
                padding: 0;
                font-weight: bold;
            }
        """)
        self.register_btn.clicked.connect(self.handle_register)
        
        links_layout.addWidget(self.forgot_btn)
        links_layout.addStretch()
        links_layout.addWidget(self.register_btn)
        
        # Agregar todo al layout principal
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addLayout(links_layout)
        
        self.setLayout(layout)
    
    def handle_login(self):
        """Manejar el intento de inicio de sesión"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
        
        if self.auth_controller.login(email, password):
            self.accept()  # Cierra el diálogo con éxito
        else:
            QMessageBox.warning(self, "Error", "Correo o contraseña incorrectos")
            self.password_input.clear()
    
    def handle_forgot_password(self):
        """Manejar la recuperación de contraseña"""
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Error", "Por favor ingrese su correo electrónico")
            return
        
        if self.auth_controller.recover_password(email):
            QMessageBox.information(
                self, 
                "Correo enviado", 
                "Se ha enviado un enlace de recuperación a su correo electrónico"
            )
        else:
            QMessageBox.warning(
                self, 
                "Error", 
                "No se encontró una cuenta asociada a este correo"
            )
    
    def handle_register(self):
        """Mostrar el formulario de registro"""
        register_view = RegisterView(self)
        if register_view.exec_() == QDialog.Accepted:
            QMessageBox.information(
                self, 
                "Registro exitoso", 
                "Su cuenta ha sido creada. Ahora puede iniciar sesión"
            )
            # Autocompletar el email en el login
            self.email_input.setText(register_view.email_input.text())