from database.db_connection import create_connection

class SaleModel:
    @staticmethod
    def create_sale(usuario_id, base_inicial, total, items):
        """Crear una nueva venta con sus items"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                
                # Insertar la venta principal
                cursor.execute(
                    "INSERT INTO ventas (usuario_id, base_inicial, total) VALUES (?, ?, ?)",
                    (usuario_id, base_inicial, total)
                )
                sale_id = cursor.lastrowid
                
                # Insertar los items de la venta
                for item in items:
                    producto_id, cantidad, precio_unitario, subtotal = item
                    cursor.execute(
                        """INSERT INTO detalle_venta 
                        (venta_id, producto_id, cantidad, precio_unitario, subtotal) 
                        VALUES (?, ?, ?, ?, ?)""",
                        (sale_id, producto_id, cantidad, precio_unitario, subtotal)
                    )
                
                conn.commit()
                return sale_id
            except Exception as e:
                print(f"Error al crear venta: {e}")
                conn.rollback()
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def get_sales_by_date(start_date, end_date):
        """Obtener ventas por rango de fechas"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT id, fecha, base_inicial, total 
                    FROM ventas 
                    WHERE date(fecha) BETWEEN date(?) AND date(?)
                    ORDER BY fecha DESC""",
                    (start_date, end_date)
                )
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener ventas: {e}")
                return []
            finally:
                conn.close()
        return []

    @staticmethod
    def get_sale_details(sale_id):
        """Obtener detalles de una venta específica"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                
                # Obtener información de la venta
                cursor.execute(
                    "SELECT fecha, base_inicial, total FROM ventas WHERE id = ?",
                    (sale_id,)
                )
                sale_info = cursor.fetchone()
                
                if not sale_info:
                    return None
                
                # Obtener items de la venta
                cursor.execute(
                    """SELECT p.nombre, dv.cantidad, dv.precio_unitario, dv.subtotal 
                    FROM detalle_venta dv
                    JOIN productos p ON dv.producto_id = p.id
                    WHERE dv.venta_id = ?""",
                    (sale_id,)
                )
                items = cursor.fetchall()
                
                return {
                    'fecha': sale_info[0],
                    'base_inicial': sale_info[1],
                    'total': sale_info[2],
                    'items': items
                }
            except Exception as e:
                print(f"Error al obtener detalles de venta: {e}")
                return None
            finally:
                conn.close()
        return None
    
    def clear_all_sales(self):
        """Eliminar todo el historial de ventas"""
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM detalle_venta")
                cursor.execute("DELETE FROM ventas")
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al borrar historial: {e}")
                return False
            finally:
                conn.close()
        return False
        