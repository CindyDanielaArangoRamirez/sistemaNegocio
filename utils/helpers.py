import sys # Necesario para sys._MEIPASS y sys.executable
import os  # Necesario para os.path.abspath, os.path.join, os.path.dirname
from PyQt5.QtWidgets import QMessageBox


def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona en desarrollo y para PyInstaller. """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        current_dir = os.path.dirname(os.path.abspath(__file__)) # Directorio de helpers.py (utils/)
        base_path = os.path.abspath(os.path.join(current_dir, "..")) # Sube un nivel a la raíz del proyecto

    final_path = os.path.join(base_path, relative_path)
    # print(f"DEBUG resource_path: relative='{relative_path}', base='{base_path}', final='{final_path}', exists={os.path.exists(final_path)}") # Para depuración
    return final_path

def show_error(message, parent=None):
    """Mostrar mensaje de error"""
    QMessageBox.critical(parent, "Error", message)

def show_success(message, parent=None):
    """Mostrar mensaje de éxito"""
    QMessageBox.information(parent, "Éxito", message)

def validate_number(input_str):
    """Validar si una cadena es un número válido"""
    try:
        float(input_str)
        return True
    except ValueError:
        return False
    



def show_error(message, parent=None):
    """Mostrar mensaje de error"""
    QMessageBox.critical(parent, "Error", message)

def show_success(message, parent=None):
    """Mostrar mensaje de éxito"""
    QMessageBox.information(parent, "Éxito", message)

def validate_number(input_str):
    """Validar si una cadena es un número válido"""
    try:
        float(input_str)
        return True
    except ValueError:
        return False