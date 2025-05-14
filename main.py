import sys
import threading
from PyQt5.QtWidgets import QApplication, QDialog # Asegúrate que QDialog esté importado
from database.db_connection import initialize_database
import uvicorn

# --- Manejo de sys.path para importación de API ---
# Esto es importante si ejecutas main.py desde la raíz y api es un subdirectorio
# o si uvicorn tiene problemas para encontrar 'api.main'.
# Si 'api' está en el mismo nivel que 'main.py' o en PYTHONPATH, esto podría no ser necesario.
# Comenta/descomenta según tu estructura y cómo ejecutes.
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(current_dir)
# --- Fin Manejo de sys.path ---

try:
    from api.main import app as fastapi_app
except ImportError as e:
    print(f"Error importando fastapi_app: {e}")
    print("Asegúrate de que la API esté accesible desde main.py (PYTHONPATH o estructura de directorios).")
    sys.exit(1) # Salir si no se puede importar la API


def run_api():
    """Ejecutar la API FastAPI en segundo plano"""
    # El host "0.0.0.0" hace que sea accesible desde otras máquinas en la red.
    # Si es solo local, "127.0.0.1" es suficiente.
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info") # Cambiado a 127.0.0.1 y añadido log_level

if __name__ == "__main__":
    print("Iniciando aplicación de ferretería...")

    # 1. Inicializar la base de datos primero
    print("Inicializando base de datos...")
    initialize_database()
    print("Base de datos lista.")
    
    # 2. Iniciar API en un hilo separado
    print("Iniciando API en segundo plano...")
    api_thread = threading.Thread(target=run_api, name="FastAPIThread")
    api_thread.daemon = True  # Permite que el programa principal termine aunque el hilo siga corriendo
    api_thread.start()
    print(f"API debería estar corriendo en http://127.0.0.1:8000")
    
    # 3. Iniciar aplicación principal PyQt
    print("Iniciando aplicación PyQt...")
    app_pyqt = QApplication(sys.argv) # Renombrada la variable para evitar confusión con fastapi_app
    
    # Cargar estilos CSS
    try:
        with open('styles/styles.css', 'r') as f:
            app_pyqt.setStyleSheet(f.read())
        print("Estilos CSS cargados.")
    except FileNotFoundError:
        print("Advertencia: styles/styles.css no encontrado. Se usarán estilos por defecto de PyQt.")
    except Exception as e:
        print(f"Error al cargar styles.css: {e}")

    # Importar LoginView aquí para evitar problemas de importación circular si LoginView importa MainWindow
    from app.views.login_view import LoginView
    
    login_dialog = LoginView()
    print("Mostrando diálogo de inicio de sesión...")
    
    # login_dialog.exec_() es bloqueante. El código espera hasta que el diálogo se cierre.
    login_result = login_dialog.exec_()

    if login_result == QDialog.Accepted: # Usar la constante de QDialog
        print("Login aceptado. Iniciando ventana principal...")
        # Importar MainWindow aquí, después de que LoginView haya terminado y QApplication esté activa
        from app.views.main_window import MainWindow
        
        # Obtener los datos del usuario que se guardaron en login_dialog
        # Asegúrate que LoginView tenga un atributo como 'user_logged_in_data'
        if hasattr(login_dialog, 'user_logged_in_data') and login_dialog.user_logged_in_data:
            user_data_for_main_window = login_dialog.user_logged_in_data
            
            main_app_window = MainWindow(user_data_for_main_window) # Pasar los datos
            main_app_window.show()
            
            print("Ventana principal mostrada. Entrando al bucle de eventos de PyQt.")
            exit_code = app_pyqt.exec_()
            print(f"Aplicación PyQt terminada con código: {exit_code}")
            sys.exit(exit_code)
        else:
            print("Error: Login fue aceptado pero no se encontraron datos del usuario. Saliendo.")
            sys.exit(1) # Salir con error si no hay datos de usuario
    else:
        print("Login cancelado o fallido. Saliendo de la aplicación.")
        sys.exit(0) # Salir de la aplicación si el login no fue exitoso