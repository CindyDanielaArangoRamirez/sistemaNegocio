from database.db_connection import create_connection

class SaleModel:
    @staticmethod
    def create_sale(user_id, initial_cash, total_amount, items):
        """
        Crea una nueva venta y sus items.
        items: lista de diccionarios, cada uno con:
               {'product_id': id, 'quantity_sold': cant, 'price_per_unit': precio_venta_actual}
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # 1. Crear la venta principal
                cursor.execute(
                    "INSERT INTO sales (user_id, initial_cash, total_amount) VALUES (?, ?, ?)",
                    (user_id, initial_cash, total_amount)
                )
                sale_id = cursor.lastrowid
                conn.commit() # Cometer la venta principal primero para obtener el sale_id

                # 2. Insertar los items de la venta y actualizar stock
                if sale_id:
                    for item in items:
                        subtotal = item['quantity_sold'] * item['price_per_unit']
                        cursor.execute(
                            """INSERT INTO sale_items
                               (sale_id, product_id, quantity_sold, price_per_unit, subtotal)
                               VALUES (?, ?, ?, ?, ?)""",
                            (sale_id, item['product_id'], item['quantity_sold'], item['price_per_unit'], subtotal)
                        )
                        # Actualizar stock del producto (llamando a la función de ProductModel o directamente)
                        # Es mejor tener la lógica de update_stock en ProductModel y llamarla
                        # from app.models.product_model import ProductModel (cuidado con imports circulares)
                        # ProductModel.update_stock(item['product_id'], item['quantity_sold'])
                        # O directamente aquí si se prefiere, pero centralizar es mejor:
                        cursor.execute(
                           "UPDATE products SET quantity_available = quantity_available - ? WHERE id = ?",
                           (item['quantity_sold'], item['product_id'])
                        )
                    conn.commit() # Cometer todos los items y actualizaciones de stock
                    return sale_id
                else:
                    conn.rollback() # Si no se pudo crear la venta, deshacer
                    return None

            except Exception as e:
                print(f"Error creating sale: {e}")
                if conn: # Asegurarse que la conexión existe antes de rollback
                    conn.rollback()
                return None
            finally:
                if conn:
                    conn.close()
        return None

    @staticmethod
    def get_sales_history_grouped_by_date():
        conn = create_connection()
        if not conn:
            return {}
        try:
            cursor = conn.cursor()
            # Usar STRFTIME para agrupar por día, y los nombres de columna correctos
            query = """
            SELECT
                s.id as sale_id,
                STRFTIME('%Y-%m-%d', s.sale_timestamp) as sale_date_group,
                s.initial_cash,
                si.product_id,
                p.name as product_name,
                p.purchase_price,
                p.sale_price as product_current_sale_price, -- Precio actual del producto, puede ser diferente al de la venta
                si.quantity_sold,
                si.price_per_unit as price_at_sale -- Precio al que se vendió
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            JOIN products p ON si.product_id = p.id
            ORDER BY s.sale_timestamp DESC, s.id ASC, p.name ASC;
            """
            # Nota: sale_timestamp ya incluye la hora, STRFTIME('%Y-%m-%d', s.sale_timestamp) la trunca a día.
            cursor.execute(query)
            raw_sales_data = cursor.fetchall()

            history_by_date = {}
            daily_base_cache = {} # Para almacenar la base_inicial por día

            for row in raw_sales_data:
                date_str = row['sale_date_group']

                # Almacenar/recuperar la base inicial para ese día
                # Asumimos que la base_inicial es la misma para todas las ventas de un mismo día
                # o que la tomamos de la primera venta registrada para ese día.
                # Una mejor aproximación sería tener una tabla separada para 'bases diarias'.
                # Por ahora, si múltiples ventas en un día tienen diferentes 'initial_cash',
                # esta lógica tomará la de la primera que procese para esa fecha.
                if date_str not in daily_base_cache:
                    # Podríamos hacer una subconsulta para obtener la base_inicial de la primera venta del día
                    # o simplemente tomar la que viene con la primera fila que encontremos para esa fecha.
                    # Aquí, la tomaremos de la fila actual la primera vez que veamos la fecha.
                    daily_base_cache[date_str] = row['initial_cash']


                if date_str not in history_by_date:
                    history_by_date[date_str] = {
                        'base_amount': daily_base_cache[date_str], # Usar la base cacheada
                        'items': [],
                        'total_day_sales_value': 0, # Valor total de ventas del día
                        'total_day_cost_value': 0   # Costo total de los productos vendidos ese día
                    }

                item_total_sale_price = row['quantity_sold'] * row['price_at_sale']
                item_total_cost_price = row['quantity_sold'] * row['purchase_price'] # Costo basado en el precio de compra

                history_by_date[date_str]['items'].append({
                    'sale_id': row['sale_id'], # Puede ser útil para depurar o enlazar
                    'product_name': row['product_name'],
                    'quantity': row['quantity_sold'],
                    'unit_sale_price_at_transaction': row['price_at_sale'],
                    'total_sale_price': item_total_sale_price,
                    'unit_purchase_price': row['purchase_price'], # Para referencia
                    'total_cost_price': item_total_cost_price # Para referencia
                })
                history_by_date[date_str]['total_day_sales_value'] += item_total_sale_price
                history_by_date[date_str]['total_day_cost_value'] += item_total_cost_price

            # Calcular ganancias netas por día
            for date_str, data in history_by_date.items():
                data['net_profit'] = data['total_day_sales_value'] - data['total_day_cost_value']

            return history_by_date

        except Exception as e:
            print(f"Error fetching sales history: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def delete_all_sales_history():
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Borrar en orden para respetar las FK
                cursor.execute("DELETE FROM sale_items;")
                cursor.execute("DELETE FROM sales;")
                # Si tuvieras una tabla de 'bases diarias' independiente, borrarla también.
                conn.commit()
                return True
            except Exception  as e:
                print(f"Error deleting sales history: {e}")
                if conn:
                    conn.rollback()
                return False
            finally:
                conn.close()
        return False

    # Puedes añadir más funciones, como obtener ventas por rango de fechas, etc.
    # @staticmethod
    # def get_sales_by_date_range(start_date, end_date):
    #     # ...similar a get_sales_history_grouped_by_date pero con un WHERE para las fechas...
    #     pass