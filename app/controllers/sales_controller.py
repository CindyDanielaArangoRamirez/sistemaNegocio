from models.sale_model import SaleModel
from models.product_model import ProductModel
from utils.helpers import show_error, show_success

class SalesController:
    def __init__(self):
        self.sale_model = SaleModel()
        self.product_model = ProductModel()
    
    def create_sale(self, user_id, base, items):
        """Crear una nueva venta"""
        if not items:
            show_error("No hay productos en la venta")
            return False
            
        # Calcular total
        total = sum(item['subtotal'] for item in items)
        
        # Preparar items para la base de datos
        db_items = [
            (item['id'], item['quantity'], item['price'], item['subtotal']) 
            for item in items
        ]
        