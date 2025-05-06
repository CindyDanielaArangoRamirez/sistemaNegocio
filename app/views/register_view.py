from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt
from app.controllers.auth_controller import AuthController

class RegisterView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_controller = AuthController()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Registro de Usuario")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        title = QLabel("Crear Cuenta")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        # Campos del formulario
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre completo")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmar contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        
        # Botones
        buttons_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.register_btn = QPushButton("Registrarme")
        self.register_btn.clicked.connect(self.handle_register)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.register_btn)
        
        # Estilos
        for input_field in [self.name_input, self.email_input, 
                          self.password_input, self.confirm_password_input]:
            input_field.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        # Agregar al layout
        layout.addWidget(title)
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Correo:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Confirmar contraseña:"))
        layout.addWidget(self.confirm_password_input)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def handle_register(self):
        """Validar y registrar nuevo usuario"""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validaciones
        if not all([name, email, password, confirm_password]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return
            
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 6 caracteres")
            return
            
        if self.auth_controller.email_exists(email):
            QMessageBox.warning(self, "Error", "Este correo ya está registrado")
            return
            
        # Registrar usuario
        if self.auth_controller.register(name, email, password):
            QMessageBox.information(self, "Éxito", "Registro completado exitosamente")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Ocurrió un error al registrar el usuario")