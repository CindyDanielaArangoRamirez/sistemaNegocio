# app/views/register_view.py
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QApplication # QFrame y QApplication para el estilo
)
from PyQt5.QtCore import Qt

# Importar el controlador actualizado
from app.controllers.auth_controller import AuthController # AuthController es una clase con métodos estáticos

class RegisterView(QDialog): # QDialog es apropiado para una ventana de registro
    def __init__(self, parent=None):
        super().__init__(parent)
        # No necesitas instanciar AuthController si sus métodos son estáticos
        # self.auth_controller = AuthController()
        self.init_ui()
        # self.load_styles() # Si cargas estilos desde un archivo CSS global

    def init_ui(self):
        self.setWindowTitle("Registro de Nuevo Usuario")
        # Quitar setFixedSize para que el estilo de pantalla completa/contenedor central funcione si lo aplicas
        # self.setFixedSize(400, 450) # Ajustar tamaño si es necesario

        # --- Aplicar estilo de pantalla completa y contenedor central (opcional, como en LoginView) ---
        # Esto es si quieres que la ventana de registro tenga el mismo estilo que LoginView
        # Si es un diálogo simple, puedes omitir esta parte de showFullScreen.
        # screen_geometry = QApplication.primaryScreen().geometry()
        # self.setGeometry(screen_geometry)
        # self.showFullScreen() # Ocupar toda la pantalla
        # self.setStyleSheet("background-color: #2c3e50;") # Color azul oscuro para el fondo

        # Contenedor central blanco (si usas el estilo de pantalla completa)
        # self.central_container = QFrame(self)
        # self.central_container.setObjectName("authContainer")
        # self.central_container.setStyleSheet("""
        #     QFrame#authContainer {
        #         background-color: white;
        #         border-radius: 20px;
        #         max-width: 450px; /* Ancho máximo del recuadro */
        #         /* min-height: 400px; /* Altura mínima */
        #         padding: 30px;
        #     }
        # """)
        # container_layout = QVBoxLayout(self.central_container) # Layout para el contenido del recuadro

        # Si es un diálogo normal, usa un layout principal directamente en el QDialog
        main_dialog_layout = QVBoxLayout(self) # Usar este si no es pantalla completa
        main_dialog_layout.setContentsMargins(30, 30, 30, 30)
        main_dialog_layout.setSpacing(15)
        # --- Fin Estilo Pantalla Completa ---

        title_label = QLabel("Crear Nueva Cuenta")
        title_label.setObjectName("authTitle") # Para CSS
        title_label.setAlignment(Qt.AlignCenter)
        # Si no usas el contenedor central, añade a main_dialog_layout:
        main_dialog_layout.addWidget(title_label)
        # Si usas contenedor central, añade a container_layout:
        # container_layout.addWidget(title_label)

        # --- Campos del Formulario ---
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de usuario (para iniciar sesión)")
        self.username_input.setObjectName("authInput")
        main_dialog_layout.addWidget(QLabel("Nombre de Usuario:")) # Etiqueta actualizada
        main_dialog_layout.addWidget(self.username_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setObjectName("authInput")
        main_dialog_layout.addWidget(QLabel("Correo Electrónico:"))
        main_dialog_layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mínimo 6 caracteres")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("authInput")
        main_dialog_layout.addWidget(QLabel("Contraseña:"))
        main_dialog_layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Repita la contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setObjectName("authInput")
        main_dialog_layout.addWidget(QLabel("Confirmar Contraseña:"))
        main_dialog_layout.addWidget(self.confirm_password_input)

        # --- Botones ---
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch() # Empujar botones a la derecha si se desea
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("authButtonSecondary") # Estilo para botón secundario
        self.cancel_button.clicked.connect(self.reject) # reject() cierra el QDialog
        buttons_layout.addWidget(self.cancel_button)

        self.register_button = QPushButton("Registrarme")
        self.register_button.setObjectName("authButtonPrimary") # Estilo para botón principal
        self.register_button.clicked.connect(self.handle_registration_attempt)
        buttons_layout.addWidget(self.register_button)
        
        main_dialog_layout.addStretch(1) # Añadir espacio antes de los botones
        main_dialog_layout.addLayout(buttons_layout)

        # --- Aplicar estilos (si no usas un CSS global cargado en main.py o MainWindow) ---
        # Estos son ejemplos, idealmente estarían en tu styles.css
        if not self.styleSheet(): # Solo aplicar si no hay un stylesheet global ya aplicado
            title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 15px;")
            for input_widget in [self.username_input, self.email_input, self.password_input, self.confirm_password_input]:
                input_widget.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 10pt;")
            
            self.register_button.setStyleSheet("""
                QPushButton#authButtonPrimary {
                    padding: 10px 15px; background-color: #2ecc71; /* Verde */ color: white;
                    border: none; border-radius: 5px; font-weight: bold; font-size: 10pt;
                }
                QPushButton#authButtonPrimary:hover { background-color: #27ae60; }
            """)
            self.cancel_button.setStyleSheet("""
                QPushButton#authButtonSecondary {
                    padding: 10px 15px; background-color: #bdc3c7; /* Gris */ color: #333;
                    border: none; border-radius: 5px; font-size: 10pt;
                }
                QPushButton#authButtonSecondary:hover { background-color: #95a5a6; }
            """)
        # --- Fin Aplicar Estilos ---

        # --- Si usas el contenedor central blanco para estilo de pantalla completa ---
        # if hasattr(self, 'central_container'):
        #     # Crear el layout principal para la ventana del diálogo
        #     # que centrará el 'central_container'
        #     outer_layout = QVBoxLayout(self)
        #     outer_layout.addWidget(self.central_container, 0, Qt.AlignCenter)
        #     self.setLayout(outer_layout)
        # else:
        #     # Si es un diálogo normal, ya establecimos main_dialog_layout
        #     self.setLayout(main_dialog_layout) # Esto ya está hecho si no hay contenedor
        
        self.setLayout(main_dialog_layout) # Asegurarse de que el layout se establece

    def handle_registration_attempt(self):
        """Valida los datos del formulario y llama al controlador para registrar."""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip().lower() # Guardar email en minúsculas es buena práctica
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # --- Validaciones ---
        if not all([username, email, password, confirm_password]):
            QMessageBox.warning(self, "Campos Incompletos", "Todos los campos son obligatorios.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error de Contraseña", "Las contraseñas no coinciden.")
            self.password_input.setFocus()
            self.password_input.selectAll()
            return

        if len(password) < 6: # O la longitud que definas como mínima
            QMessageBox.warning(self, "Contraseña Débil", "La contraseña debe tener al menos 6 caracteres.")
            self.password_input.setFocus()
            return
        
        # Validar formato de email (básico)
        if "@" not in email or "." not in email.split('@')[-1]:
            QMessageBox.warning(self, "Email Inválido", "Por favor, ingrese un correo electrónico válido.")
            self.email_input.setFocus()
            return

        # Llamar al AuthController (método estático)
        # AuthController.register_user debería devolver el ID del usuario si tiene éxito, o None/False si falla.
        # También debería manejar internamente la verificación de si el email o username ya existen.
        user_id_or_error = AuthController.register_user(username, email, password)

        if isinstance(user_id_or_error, int): # Asumiendo que devuelve el ID en éxito
            QMessageBox.information(self, "Registro Exitoso",
                                    f"¡Usuario '{username}' registrado correctamente!\n"
                                    "Ahora puede iniciar sesión.")
            self.accept() # Cierra el diálogo de registro con resultado aceptado
        else:
            # AuthController.register_user debería devolver None o un mensaje de error específico
            # si la validación (ej. email/username ya existe) falla en el controlador/modelo.
            error_message = "Ocurrió un error desconocido durante el registro."
            if user_id_or_error == "EMAIL_EXISTS": # Ejemplo de código de error
                error_message = "El correo electrónico ingresado ya está registrado."
                self.email_input.setFocus()
            elif user_id_or_error == "USERNAME_EXISTS": # Ejemplo
                error_message = "El nombre de usuario ingresado ya existe. Por favor, elija otro."
                self.username_input.setFocus()
            # Podrías tener más códigos de error del controlador.
            
            QMessageBox.critical(self, "Error de Registro", error_message)