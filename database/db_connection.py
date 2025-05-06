import sqlite3
from sqlite3 import Error
import os

def create_connection():
    """Crear conexión a la base de datos SQLite"""
    os.makedirs('database', exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect('database/database.db')
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Error as e:
        print(f"Error al conectar a SQLite: {e}")
        return None

def initialize_database():
    """Inicializar la base de datos con tablas"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Tabla usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla productos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    cantidad_disponible REAL NOT NULL,
                    precio_unitario REAL NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla ventas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                    base_inicial REAL NOT NULL,
                    total REAL NOT NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
            
            # Tabla detalle_venta
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detalle_venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad REAL NOT NULL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            """)
            
            # Verificar si existe el usuario admin
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] == 0:
                # Crear usuario admin por defecto (contraseña: admin)
                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
                    ("Admin", "admin@ferreteria.com", "21232f297a57a5a743894a0e4a801fc3")
                )
            
            conn.commit()
            print("Base de datos inicializada correctamente")
        except Error as e:
            print(f"Error al inicializar la base de datos: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    initialize_database()