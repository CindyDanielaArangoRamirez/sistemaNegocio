# app/controllers/auth_controller.py
from app.models.user_model import UserModel, verify_password # verify_password es un helper, pero puede estar aquí o en UserModel

class AuthController:
    @staticmethod
    def register_user(username, email, password):
        """
        Registra un nuevo usuario.
        Devuelve el ID del usuario creado o None si falla.
        """
        # Aquí podrías añadir validaciones (ej. longitud de contraseña, formato de email)
        if not username or not email or not password:
            # Manejar error de campos vacíos, quizás devolviendo un mensaje específico
            print("Error: Username, email, and password cannot be empty.")
            return None
        
        user_id = UserModel.create_user(username, email, password)
        if user_id:
            print(f"User {username} registered successfully with ID: {user_id}")
            return user_id
        else:
            # El modelo ya imprime un error, pero podrías añadir más contexto
            print(f"Failed to register user {username}.")
            return None

    @staticmethod
    def login_user(username, password):
        """
        Autentica un usuario.
        Devuelve los datos del usuario (diccionario/sqlite3.Row) si es exitoso, sino None.
        """
        if not username or not password:
            print("Error: Username and password cannot be empty.")
            return None

        user_data = UserModel.get_user_by_username(username)

        if user_data and verify_password(user_data['password_hash'], password):
            print(f"User {username} logged in successfully.")
            # Devolver solo la información necesaria para la sesión, no el hash de la contraseña
            # Por ejemplo: {'id': user_data['id'], 'username': user_data['username'], 'email': user_data['email']}
            # O todo el user_data si es conveniente y la vista maneja la no exposición del hash.
            return user_data
        else:
            print(f"Login failed for user {username}.")
            return None

    @staticmethod
    def request_password_reset(email):
        """
        Maneja la solicitud de reseteo de contraseña.
        Por ahora, solo verifica si el email existe.
        En una implementación real, generaría un token y enviaría un email.
        Devuelve los datos del usuario si el email existe, sino None.
        """
        user_data = UserModel.get_user_by_email(email)
        if user_data:
            print(f"Password reset requested for email: {email}. User found.")
            # Aquí iría la lógica de enviar email con un token de reseteo.
            # Por ahora, solo confirmamos que el usuario existe.
            return user_data # O un mensaje de éxito específico
        else:
            print(f"Password reset request for email: {email}. User not found.")
            return None

    @staticmethod
    def complete_password_reset(email, new_password):
        """
        Completa el proceso de reseteo de contraseña actualizándola en la BD.
        (Esta función es más para un flujo completo de reseteo, puede que no la uses si
         solo envías la contraseña 'olvidada' como indicaba el requerimiento original)
        Devuelve True si la contraseña se actualizó, False en caso contrario.
        """
        if not email or not new_password:
            print("Error: Email and new password cannot be empty for reset.")
            return False
        
        # Aquí faltaría la validación del token de reseteo si se implementara
        success = UserModel.update_password_by_email(email, new_password)
        if success:
            print(f"Password for email {email} has been reset successfully.")
            return True
        else:
            print(f"Failed to reset password for email {email}.")
            return False