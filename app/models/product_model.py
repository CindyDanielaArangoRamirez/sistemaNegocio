from database.db_connection import create_connection

class ProductModel:
    @staticmethod
    def create_product(nombre, cantidad, precio):
        """Crear un nuevo producto"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO productos (nombre, cantidad_disponible, precio_unitario) VALUES (?, ?, ?)",
                    (nombre, cantidad, precio)
                )
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Error al crear producto: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def get_all_products():
        """Obtener todos los productos"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, nombre, cantidad_disponible, precio_unitario FROM productos"
                )
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener productos: {e}")
                return []
            finally:
                conn.close()
        return []

    @staticmethod
    def search_products(search_term):
        """Buscar productos por nombre (autocompletado)"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, nombre, cantidad_disponible, precio_unitario FROM productos WHERE nombre LIKE ?",
                    (f'{search_term}%',)
                )
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al buscar productos: {e}")
                return []
            finally:
                conn.close()
        return []

    @staticmethod
    def get_product_by_id(product_id):
        """Obtener producto por ID"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, nombre, cantidad_disponible, precio_unitario FROM productos WHERE id = ?",
                    (product_id,)
                )
                return cursor.fetchone()
            except Exception as e:
                print(f"Error al obtener producto: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def update_product(product_id, nombre, cantidad, precio):
        """Actualizar un producto existente"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE productos 
                    SET nombre = ?, cantidad_disponible = ?, precio_unitario = ?, fecha_actualizacion = CURRENT_TIMESTAMP 
                    WHERE id = ?""",
                    (nombre, cantidad, precio, product_id)
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error al actualizar producto: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def delete_product(product_id):
        """Eliminar un producto"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM productos WHERE id = ?",
                    (product_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error al eliminar producto: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def update_stock(product_id, cantidad_vendida):
        """Actualizar el stock de un producto después de una venta"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE productos SET cantidad_disponible = cantidad_disponible - ? WHERE id = ?",
                    (cantidad_vendida, product_id)
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error al actualizar stock: {e}")
                return False
            finally:
                conn.close()
        return False