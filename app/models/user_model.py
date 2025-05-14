
from database.db_connection import create_connection # Asumiendo que db_connection.py está en el directorio 'database'
import hashlib # Para hashear contraseñas

# (Si tienes funciones de hashing separadas, asegúrate que coincidan con la lógica de abajo)
def hash_password(password):
    # Usa un método de hashing seguro como bcrypt o scrypt en producción.
    # MD5 es solo para ejemplo y porque lo usaste antes, pero es INSEGURO.
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(stored_password_hash, provided_password):
    return stored_password_hash == hash_password(provided_password)

class UserModel:
    @staticmethod
    def create_user(username, email, password):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                hashed_pass = hash_password(password) # Hashear la contraseña
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, hashed_pass)
                )
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Error creating user: {e}")
                # Podrías querer verificar si el error es por email/username duplicado (UNIQUE constraint)
                # e.g., if "UNIQUE constraint failed: users.email" in str(e):
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def get_user_by_username(username):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Seleccionar todos los campos necesarios para la autenticación y gestión
                cursor.execute(
                    "SELECT id, username, email, password_hash, registration_date FROM users WHERE username = ?",
                    (username,)
                )
                return cursor.fetchone() # Devuelve un objeto sqlite3.Row o None
            except Exception as e:
                print(f"Error fetching user by username: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def get_user_by_email(email): # Para la función "olvidé contraseña"
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, password_hash FROM users WHERE email = ?",
                    (email,)
                )
                return cursor.fetchone()
            except Exception as e:
                print(f"Error fetching user by email: {e}")
                return None
            finally:
                conn.close()
        return None

    # Si necesitas actualizar la contraseña:
    @staticmethod
    def update_password_by_email(email, new_password):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                hashed_new_pass = hash_password(new_password)
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE email = ?",
                    (hashed_new_pass, email)
                )
                conn.commit()
                return cursor.rowcount > 0 # True si se actualizó
            except Exception as e:
                print(f"Error updating password: {e}")
                return False
            finally:
                conn.close()
        return False