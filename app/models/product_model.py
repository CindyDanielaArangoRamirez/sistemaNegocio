# app/models/product_model.py
import sqlite3 # Importar para sqlite3.Error
from database.db_connection import create_connection

class ProductModel:
    @staticmethod
    def add_product(name, quantity_available, sale_price, purchase_price):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO products (name, quantity_available, sale_price, purchase_price) VALUES (?, ?, ?, ?)",
                    (name, quantity_available, sale_price, purchase_price)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Error adding product: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def get_all_products_for_management():
        """Obtener TODOS los productos (activos e inactivos) para la vista de gestión."""
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, quantity_available, sale_price, purchase_price, is_active FROM products ORDER BY name ASC"
                )
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching all products for management: {e}")
                return []
            finally:
                conn.close()
        return []

    @staticmethod
    def get_active_products_for_sale():
        """Obtener solo los productos activos (para ventas, etc.)."""
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, quantity_available, sale_price, purchase_price, is_active FROM products WHERE is_active = 1 ORDER BY name ASC"
                )
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching active products: {e}")
                return []
            finally:
                conn.close()
        return []

    @staticmethod
    def search_products_for_management(search_term):
        """Buscar TODOS los productos (activos e inactivos) por nombre para la vista de gestión."""
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, quantity_available, sale_price, purchase_price, is_active FROM products WHERE name LIKE ? ORDER BY name ASC",
                    (f"%{search_term}%",)
                )
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error searching products for management: {e}")
                return []
            finally:
                conn.close()
        return []

    @staticmethod
    def search_active_products_for_sale(search_term):
        """Buscar solo productos ACTIVOS por nombre (para ventas, etc.)."""
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, quantity_available, sale_price, purchase_price, is_active FROM products WHERE name LIKE ? AND is_active = 1 ORDER BY name ASC",
                    (f"%{search_term}%",)
                )
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error searching active products: {e}")
                return []
            finally:
                conn.close()
        return []

    @staticmethod
    def get_product_by_id(product_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, quantity_available, sale_price, purchase_price, is_active FROM products WHERE id = ?",
                    (product_id,)
                )
                return cursor.fetchone()
            except sqlite3.Error as e:
                print(f"Error fetching product by ID: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def update_product(product_id, name, quantity_available, sale_price, purchase_price):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE products
                       SET name = ?, quantity_available = ?, sale_price = ?, purchase_price = ?
                       WHERE id = ?""",
                    (name, quantity_available, sale_price, purchase_price, product_id)
                )
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error updating product: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def soft_delete_product(product_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE products SET is_active = 0 WHERE id = ?", (product_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error soft deleting product: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def restore_product(product_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE products SET is_active = 1 WHERE id = ?", (product_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error restoring product: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def update_stock(product_id, quantity_sold):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE products SET quantity_available = quantity_available - ? WHERE id = ?",
                    (quantity_sold, product_id)
                )
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error updating stock: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def get_low_stock_products(threshold=0):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, quantity_available, is_active FROM products WHERE quantity_available <= ? AND is_active = 1 ORDER BY quantity_available ASC, name ASC",
                    (threshold,)
                )
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching low stock products: {e}")
                return []
            finally:
                conn.close()
        return []