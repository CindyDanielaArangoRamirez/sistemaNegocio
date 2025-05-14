# app/controllers/sales_controller.py
from app.models.sale_model import SaleModel
# from app.models.product_model import ProductModel # Podría necesitarse si la actualización de stock se maneja aquí explícitamente

class SalesController:
    current_base_cash = 0.0 # Para almacenar la base del día
    current_user_id = None # Para almacenar el ID del usuario logueado

    @classmethod
    def set_daily_base(cls, amount, user_id):
        """
        Establece la base inicial para las ventas del día y el usuario.
        """
        # Aquí podrías tener lógica para guardar esta base en una tabla `daily_cash_entries` si fuera necesario.
        # Por ahora, la almacenamos en la clase y se pasa al crear la venta.
        if amount < 0:
            print("Error: Initial cash base cannot be negative.")
            return False
        cls.current_base_cash = amount
        cls.current_user_id = user_id # Asumiendo que el user_id viene de la sesión/login
        print(f"Daily base set to: {amount} for user ID: {user_id}")
        return True

    @staticmethod
    def process_new_sale(items_to_sell, total_sale_amount, customer_payment_amount=None, change_given=None):
        """
        Procesa y registra una nueva venta.
        items_to_sell: lista de diccionarios como:
                       [{'product_id': id, 'name': 'ProdName', 'quantity_sold': qty, 'price_per_unit': price_at_sale}, ...]
        total_sale_amount: el total calculado de la venta.
        """
        if not SalesController.current_user_id:
            print("Error: No user logged in to process sale.")
            # Podrías lanzar una excepción o devolver un código de error específico.
            return None
        
        if SalesController.current_base_cash is None: # O alguna validación de que se haya ingresado.
             print("Error: Daily cash base has not been set.")
             return None

        if not items_to_sell:
            print("Error: No items to sell.")
            return None

        # Preparar los items para el SaleModel.create_sale
        # SaleModel espera: {'product_id': id, 'quantity_sold': cant, 'price_per_unit': precio_venta_actual}
        # La información adicional como 'name' en items_to_sell es para la vista, no para el modelo de venta.
        model_items = [
            {
                'product_id': item['product_id'],
                'quantity_sold': item['quantity_sold'],
                'price_per_unit': item['price_per_unit']
            }
            for item in items_to_sell
        ]

        sale_id = SaleModel.create_sale(
            user_id=SalesController.current_user_id,
            initial_cash=SalesController.current_base_cash, # Pasa la base establecida
            total_amount=total_sale_amount,
            items=model_items
        )

        if sale_id:
            print(f"Sale ID {sale_id} processed successfully.")
            # Aquí es donde se podría interactuar con la impresora, pasando
            # items_to_sell (que tiene más detalles como el nombre), total_sale_amount,
            # customer_payment_amount, change_given.
            # La impresión es una tarea de la vista o de un servicio de utilidad.
            return sale_id
        else:
            print("Failed to process sale.")
            return None

    # La generación de factura/recibo y la impresión son más responsabilidad de la vista
    # o de un módulo de utilidades (como tu utils/printer.py),
    # pero el controlador puede orquestar la obtención de los datos.