from database.db_connection import create_connection

class UserModel:
    @staticmethod
    def create_user(nombre, email, password):
        """Crear un nuevo usuario en la base de datos"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
                    (nombre, email, password)
                )
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Error al crear usuario: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def get_user_by_email(email):
        """Obtener usuario por email"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, nombre, email, password FROM usuarios WHERE email = ?",
                    (email,)
                )
                return cursor.fetchone()
            except Exception as e:
                print(f"Error al obtener usuario: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def email_exists(email):
        """Verificar si un email ya está registrado"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM usuarios WHERE email = ?",
                    (email,)
                )
                return cursor.fetchone()[0] > 0
            except Exception as e:
                print(f"Error al verificar email: {e}")
                return False
            finally:
                conn.close()
        return False