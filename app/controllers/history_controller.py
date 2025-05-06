from app.models.sale_model import SaleModel
from datetime import datetime, timedelta

class HistoryController:
    def __init__(self):
        self.sale_model = SaleModel()

    def get_sales_by_date_range(self, start_date, end_date):
        """Obtener ventas por rango de fechas"""
        try:
            # Ajustar las fechas para incluir todo el día final
            end_date = (datetime.strptime(end_date, "%Y-%m-%d") + 
                       timedelta(days=1)).strftime("%Y-%m-%d")
            return self.sale_model.get_sales_by_date(start_date, end_date)
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return []

    def get_sale_details(self, sale_id):
        """Obtener detalles de una venta específica"""
        try:
            return self.sale_model.get_sale_details(sale_id)
        except Exception as e:
            print(f"Error al obtener detalles de venta: {e}")
            return None