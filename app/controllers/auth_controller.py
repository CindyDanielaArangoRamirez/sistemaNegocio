from ..models.user_model import UserModel  # Usando importación relativa
import hashlib

class AuthController:
    def __init__(self):
        self.user_model = UserModel()
    
    def login(self, email, password):
        """Autenticar usuario"""
        user = self.user_model.get_user_by_email(email)
        if user:
            _, _, _, stored_password = user
            if self._hash_password(password) == stored_password:
                return True
        return False
    
    def email_exists(self, email):
        """Verificar si un email ya está registrado"""
        return self.user_model.email_exists(email)
    
    
    def recover_password(self, email):
        """Recuperar contraseña (simulado)"""
        return self.user_model.email_exists(email)
    
    def register(self, nombre, email, password):
        """Registrar nuevo usuario"""
        if not nombre or not email or not password:
            return False
            
        if self.user_model.email_exists(email):
            return False
            
        hashed_password = self._hash_password(password)
        return self.user_model.create_user(nombre, email, hashed_password) is not None
    
    def _hash_password(self, password):
        """Hashear contraseña con SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()