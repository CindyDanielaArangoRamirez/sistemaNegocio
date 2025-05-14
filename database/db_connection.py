
import sqlite3
from sqlite3 import Error as SQLiteError # Importar Error como SQLiteError para evitar confusión
import os
import hashlib

def create_connection():
    """Crear conexión a la base de datos SQLite"""
    os.makedirs('database', exist_ok=True)
    conn = None
    try:
        db_path = os.path.join('database', 'database.db')
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row # Correcto
        return conn
    except SQLiteError as e: # Usar SQLiteError
        print(f"Error al conectar a SQLite: {e}")
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
            
            # Cometer la creación de todas las tablas ANTES de intentar insertar datos
            conn.commit()
            print("Tablas creadas/verificadas.")

            # Verificar e insertar el usuario admin (usando la tabla 'users')
            print("Verificando usuario admin...")
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'Admin'")
            admin_exists = cursor.fetchone() # fetchone() devuelve None si no hay filas, o un Row/tuple
            
            if admin_exists is not None and admin_exists[0] == 0: # Comprobar si no es None y si el count es 0
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
            else: # Caso raro, fetchone() devolvió None pero no debería con COUNT(*)
                print("Advertencia: No se pudo determinar si el usuario admin existe (consulta COUNT devolvió None).")

            # Commit final para asegurar que el admin se guarde si se creó
            conn.commit()
            print("Base de datos inicializada correctamente.")

        except SQLiteError as e: # Usar SQLiteError
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
    db_file_path = os.path.join('database', 'database.db')
    # Descomenta la siguiente línea SOLO si quieres borrar la BD cada vez que ejecutas este script directamente
    # if os.path.exists(db_file_path):
    #     os.remove(db_file_path)
    #     print(f"Archivo de base de datos '{db_file_path}' borrado para reinicialización.")
    initialize_database()