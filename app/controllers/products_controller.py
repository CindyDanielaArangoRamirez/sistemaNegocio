# app/controllers/products_controller.py
from app.models.product_model import ProductModel # Asegúrate que la ruta de importación sea correcta

class ProductsController:
    @staticmethod
    def add_new_product(name, quantity_available, sale_price, purchase_price):
        """
        Añade un nuevo producto a la base de datos.
        Llama a ProductModel.add_product.
        Devuelve el ID del producto creado o None si falla.
        """
        # Aquí se podrían añadir validaciones de datos del controlador antes de llamar al modelo,
        # aunque muchas validaciones básicas de tipo/rango ya están en los Pydantic Schemas si usas la API.
        # Para la app de escritorio, las vistas o el controlador pueden hacer estas validaciones.
        if not name or quantity_available < 0 or sale_price <= 0 or purchase_price < 0:
            print("Error (Controller): Datos de producto inválidos para agregar.")
            return None # O lanzar una excepción específica
        
        return ProductModel.add_product(name, quantity_available, sale_price, purchase_price)

    @staticmethod
    def get_all_products_for_management_view(): # Renombrado para claridad
        """
        Obtiene TODOS los productos (activos e inactivos) para la vista de gestión de productos.
        Llama a ProductModel.get_all_products_for_management.
        """
        return ProductModel.get_all_products_for_management()

    @staticmethod
    def search_products_for_management_view(search_term): # Renombrado para claridad
        """
        Busca entre TODOS los productos (activos e inactivos) para la vista de gestión.
        Llama a ProductModel.search_products_for_management.
        """
        return ProductModel.search_products_for_management(search_term)

    @staticmethod
    def get_active_products_for_sales_view():
        """
        Obtiene solo los productos ACTIVOS, típicamente para la vista de ventas (ej. autocompletado).
        Llama a ProductModel.get_active_products_for_sale.
        """
        return ProductModel.get_active_products_for_sale()

    @staticmethod
    def search_active_products_for_sales_view(search_term):
        """
        Busca solo entre productos ACTIVOS, típicamente para la vista de ventas.
        Llama a ProductModel.search_active_products_for_sale.
        """
        # Podrías añadir una verificación para search_term vacío si quieres que devuelva todos los activos.
        # if not search_term:
        #     return ProductModel.get_active_products_for_sale()
        return ProductModel.search_active_products_for_sale(search_term)

    @staticmethod
    def get_product_details(product_id):
        """
        Obtiene los detalles completos de un producto específico por su ID,
        incluyendo su estado 'is_active'.
        Llama a ProductModel.get_product_by_id.
        """
        return ProductModel.get_product_by_id(product_id)

    @staticmethod
    def update_existing_product(product_id, name, quantity_available, sale_price, purchase_price):
        """
        Actualiza los datos de un producto existente.
        No modifica el estado 'is_active' directamente; eso se maneja con activate/deactivate.
        Llama a ProductModel.update_product.
        Devuelve True si fue exitoso, False en caso contrario.
        """
        if not name or quantity_available < 0 or sale_price <= 0 or purchase_price < 0:
            print("Error (Controller): Datos de producto inválidos para actualizar.")
            return False
            
        return ProductModel.update_product(product_id, name, quantity_available, sale_price, purchase_price)

    @staticmethod
    def deactivate_product(product_id): # Renombrado de remove_product para más claridad semántica
        """
        Marca un producto como inactivo (soft delete).
        Llama a ProductModel.soft_delete_product.
        Devuelve True si fue exitoso, False en caso contrario.
        """
        # Podrías verificar si el producto existe antes de intentar desactivarlo,
        # aunque el modelo ya podría manejarlo devolviendo rowcount = 0.
        # product = ProductModel.get_product_by_id(product_id)
        # if not product:
        #     print(f"Error (Controller): Producto ID {product_id} no encontrado para desactivar.")
        #     return False
        # if not product['is_active']:
        #     print(f"Info (Controller): Producto ID {product_id} ya está inactivo.")
        #     return True # O False si consideras que no se hizo un cambio
            
        return ProductModel.soft_delete_product(product_id)

    @staticmethod
    def activate_product(product_id): # Renombrado de restore_existing_product
        """
        Reactiva un producto previamente marcado como inactivo.
        Llama a ProductModel.restore_product.
        Devuelve True si fue exitoso, False en caso contrario.
        """
        # product = ProductModel.get_product_by_id(product_id)
        # if not product:
        #     print(f"Error (Controller): Producto ID {product_id} no encontrado para activar.")
        #     return False
        # if product['is_active']:
        #     print(f"Info (Controller): Producto ID {product_id} ya está activo.")
        #     return True # O False
            
        return ProductModel.restore_product(product_id)

    @staticmethod
    def get_low_stock_products_for_alert(threshold=0):
        """
        Obtiene productos con stock bajo o igual al umbral, que estén activos.
        Llama a ProductModel.get_low_stock_products.
        """
        return ProductModel.get_low_stock_products(threshold)

    # La actualización de stock (ProductModel.update_stock) es llamada por SaleModel
    # durante el proceso de creación de una venta, por lo que generalmente no se
    # necesita un método de controlador separado para ello, a menos que tengas
    # otros flujos que modifiquen el stock directamente.