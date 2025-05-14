# app/controllers/history_controller.py
from app.models.sale_model import SaleModel

class HistoryController:
    @staticmethod
    def get_formatted_sales_history():
        """
        Obtiene el historial de ventas agrupado por fecha y formateado para la vista.
        Devuelve un diccionario donde las claves son fechas y los valores son
        diccionarios con 'base_amount', 'items', 'total_day_sales_value', 'net_profit'.
        """
        # SaleModel.get_sales_history_grouped_by_date() ya devuelve los datos bastante bien estructurados.
        # El controlador aquí podría hacer algún pre-procesamiento adicional si la vista lo necesitara,
        # pero por ahora, podemos pasar directamente los datos del modelo.
        history_data = SaleModel.get_sales_history_grouped_by_date()
        
        # Ejemplo de cómo podrías querer ordenar o transformar las fechas si no vienen ya como necesitas:
        # (Aunque el modelo ya debería ordenarlos por fecha descendente)
        # sorted_history = dict(sorted(history_data.items(), key=lambda item: item[0], reverse=True))
        # return sorted_history
        return history_data

    @staticmethod
    def clear_all_sales_history():
        """
        Elimina todo el historial de ventas.
        Devuelve True si fue exitoso, False en caso contrario.
        """
        success = SaleModel.delete_all_sales_history()
        if success:
            print("Sales history cleared successfully.")
        else:
            print("Failed to clear sales history.")
        return success

    # Si necesitas filtrar por fecha, la lógica iría aquí o en el modelo.
    # Por ejemplo:
    # @staticmethod
    # def get_sales_history_for_date(target_date_str): # target_date_str en formato 'YYYY-MM-DD'
    #     all_history = SaleModel.get_sales_history_grouped_by_date()
    #     return {target_date_str: all_history.get(target_date_str)} if target_date_str in all_history else {}