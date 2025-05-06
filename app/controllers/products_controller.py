from app.models.product_model import ProductModel
from utils.helpers import show_error, show_success

class ProductsController:
    def __init__(self):
        self.product_model = ProductModel()

    def add_product(self, name, quantity, price):
        """Agregar un nuevo producto"""
        if not name or not quantity or not price:
            show_error("Todos los campos son obligatorios")
            return False
        
        try:
            product_id = self.product_model.create_product(name, float(quantity), float(price))
            if product_id:
                show_success("Producto agregado correctamente")
                return True
            return False
        except ValueError:
            show_error("Ingrese valores numéricos válidos")
            return False
        except Exception as e:
            show_error(f"Error al agregar producto: {str(e)}")
            return False

    def update_product(self, product_id, name, quantity, price):
        """Actualizar un producto existente"""
        try:
            success = self.product_model.update_product(
                product_id, name, float(quantity), float(price)
            )
            if success:
                show_success("Producto actualizado correctamente")
            return success
        except ValueError:
            show_error("Ingrese valores numéricos válidos")
            return False
        except Exception as e:
            show_error(f"Error al actualizar producto: {str(e)}")
            return False

    def delete_product(self, product_id):
        """Eliminar un producto"""
        try:
            success = self.product_model.delete_product(product_id)
            if success:
                show_success("Producto eliminado correctamente")
            return success
        except Exception as e:
            show_error(f"Error al eliminar producto: {str(e)}")
            return False

    def search_products(self, search_term):
        """Buscar productos por nombre"""
        try:
            return self.product_model.search_products(search_term)
        except Exception as e:
            show_error(f"Error al buscar productos: {str(e)}")
            return []