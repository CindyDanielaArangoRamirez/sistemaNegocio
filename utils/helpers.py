from PyQt5.QtWidgets import QMessageBox

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