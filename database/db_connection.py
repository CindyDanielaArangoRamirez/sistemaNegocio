# PROYECTO1_FERRETERIA/database/db_connection.py

import sqlite3
from sqlite3 import Error as SQLiteError
import os
import hashlib
import sys # <--- AÑADIDO: Necesario para sys._MEIPASS

# Define el nombre del archivo de la base de datos una vez
DB_FILENAME = "database.db"

def get_persistent_db_path():
    """Obtiene una ruta persistente para la base de datos."""
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        # Aplicación empaquetada: guardar BD junto al .exe
        # o en una carpeta de datos de aplicación.
        # Opción A: Junto al .exe (más simple para portabilidad)
        application_path = os.path.dirname(sys.executable)
    else:
        # Modo desarrollo: usar la carpeta 'database' del proyecto
        application_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) # Raíz del proyecto

    db_dir = os.path.join(application_path, "database_user_data") # Nueva carpeta para datos persistentes
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, DB_FILENAME)

def create_connection():
    conn = None
    db_path_persistent = get_persistent_db_path() # <--- USA LA NUEVA FUNCIÓN
    print(f"DEBUG db_connection: Conectando a la base de datos en (persistente): {db_path_persistent}")
    try:
        conn = sqlite3.connect(db_path_persistent)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn
    except SQLiteError as e:
        print(f"Error al conectar a SQLite: {e}")
        print(f"Ruta intentada: {db_path_persistent}")
        return None
    except Exception as ex_general:
        print(f"Error general en create_connection: {ex_general}")
        print(f"Ruta (si está definida): {db_path_persistent}")
        return None

def initialize_database():
    """Inicializar la base de datos con tablas y datos por defecto si es necesario."""
    print("Intentando inicializar la base de datos...")
    conn = create_connection() 
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            print("Creando tabla 'users' (si no existe)...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            print("Creando tabla 'products' (si no existe)...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    quantity_available INTEGER NOT NULL,
                    sale_price REAL NOT NULL,
                    purchase_price REAL NOT NULL DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            print("Creando tabla 'sales' (si no existe)...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    sale_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    initial_cash REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
                )
            """)
            
            print("Creando tabla 'sale_items' (si no existe)...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity_sold INTEGER NOT NULL, 
                    price_per_unit REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
                )
            """)
            
            conn.commit()
            print("Tablas creadas/verificadas.")

            print("Verificando usuario admin...")
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'Admin'")
            admin_exists = cursor.fetchone()
            
            if admin_exists is not None and admin_exists[0] == 0:
                print("Usuario admin no encontrado, creándolo...")
                admin_password = "admin"
                hashed_password = hashlib.md5(admin_password.encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    ("Admin", "admin@ferreteria.com", hashed_password)
                )
                print("Usuario admin creado por defecto.")
            elif admin_exists is not None and admin_exists[0] > 0:
                print("Usuario admin ya existe.")
            else:
                print("Advertencia: No se pudo determinar si el usuario admin existe.")

            conn.commit()
            print("Base de datos inicializada correctamente.")

        except SQLiteError as e:
            print(f"Error al inicializar la base de datos: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
                print("Conexión a la base de datos cerrada después de inicializar.")
    else:
        print("No se pudo establecer conexión a la base de datos para inicializarla.")


if __name__ == "__main__":
    # Esta parte es para cuando ejecutas este script directamente.
    # La lógica de resource_path ya está en create_connection(), que usa initialize_database().
    
    # Si necesitas borrar la BD explícitamente ANTES de inicializar cuando ejecutas este script:
    # 1. Obtén la ruta resuelta.
    # db_relative_path_for_main = os.path.join("database", DB_FILENAME)
    # db_file_path_resolved_for_main = resource_path(db_relative_path_for_main)
    # print(f"DEBUG __main__: Ruta resuelta para la BD (si se ejecuta directamente): {db_file_path_resolved_for_main}")

    # 2. Descomenta para borrar (USA CON CUIDADO).
    # if os.path.exists(db_file_path_resolved_for_main):
    #     try:
    #         os.remove(db_file_path_resolved_for_main)
    #         print(f"Archivo de base de datos '{db_file_path_resolved_for_main}' borrado para reinicialización.")
    #     except OSError as e:
    #         print(f"Error al borrar '{db_file_path_resolved_for_main}': {e}")
            
    initialize_database()