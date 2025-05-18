# PROYECTO1_FERRETERIA/main.py
import sys
import os # Necesario para os.path.exists
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Estamos ejecutando en un bundle de PyInstaller (_MEIPASS es la carpeta temporal)
    # _MEIPASS es la raíz donde PyInstaller extrae todo.
    # Las importaciones como 'from utils.helpers import ...' deberían funcionar si 'utils'
    # está en esta raíz.
    print(f"INFO (main.py): En modo empaquetado. sys._MEIPASS: {sys._MEIPASS}")
    # Normalmente, PyInstaller ya debería configurar el path para que esto funcione.
    # Pero si hay problemas, añadir explícitamente la raíz del bundle puede ayudar.
    # if sys._MEIPASS not in sys.path:
    #    sys.path.insert(0, sys._MEIPASS) # Esta línea a veces es necesaria, a veces no.
                                        # Pruébala si el problema persiste sin ella.
else:
    # Estamos en modo desarrollo
    # Asegurar que el directorio raíz del proyecto esté en sys.path para desarrollo
    # si ejecutas main.py desde una subcarpeta o IDEs que no lo hacen por defecto.
    project_root_dev = os.path.dirname(os.path.abspath(__file__))
    if project_root_dev not in sys.path:
        sys.path.insert(0, project_root_dev)
    print(f"INFO (main.py): En modo desarrollo. project_root (dev): {project_root_dev}")
# --- FIN: AJUSTE DE SYS.PATH ---

import threading
from PyQt5.QtWidgets import QApplication, QDialog
from database.db_connection import initialize_database
from utils.helpers import resource_path # Importar la función resource_path
import uvicorn

# --- Manejo de sys.path para importación de API ---
# (Este bloque es más relevante si ejecutas 'python main.py' desde un directorio diferente
# a la raíz del proyecto, o si hay problemas para que uvicorn encuentre 'api.main'.
# Si tu estructura es PROYECTO1_FERRETERIA/main.py y PROYECTO1_FERRETERIA/api/main.py,
# usualmente no es estrictamente necesario si el CWD es la raíz del proyecto.)
# current_main_dir = os.path.dirname(os.path.abspath(__file__))
# if current_main_dir not in sys.path:
#    sys.path.append(current_main_dir) # Añadir el directorio de main.py al path

try:
    from api.main import app as fastapi_app # Intentar importar la app FastAPI
except ImportError as e:
    print(f"Error importando fastapi_app desde api.main: {e}")
    print("Asegúrate de que la API (api/main.py y sus dependencias) sea importable.")
    print("Verifica tu PYTHONPATH y la estructura de directorios.")
    sys.exit(1) # Salir si no se puede importar la API, ya que es una dependencia.


def run_api():
    """Ejecutar la API FastAPI en un hilo separado."""
    try:
        # Configuración para Uvicorn
        # log_config=None para evitar que Uvicorn configure el logging si ya lo haces tú.
        # reload=False es importante para producción/empaquetado.
        uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info", reload=False)
    except Exception as e_api:
        print(f"Error al intentar ejecutar la API con Uvicorn: {e_api}")


if __name__ == "__main__":
    print("Iniciando aplicación de ferretería...")

    # 1. Inicializar la base de datos primero
    print("Inicializando base de datos...")
    initialize_database() # Esta función ya usa resource_path internamente
    print("Base de datos lista.")
    
    # 2. Iniciar API en un hilo separado
    print("Iniciando API en segundo plano...")
    api_thread = threading.Thread(target=run_api, name="FastAPIThread", daemon=True)
    # api_thread.daemon = True # Ya está en la creación del Thread
    api_thread.start()
    print(f"API debería estar corriendo en http://127.0.0.1:8000 (puede tardar unos segundos en iniciar completamente)")
    
    # 3. Iniciar aplicación principal PyQt
    print("Iniciando aplicación PyQt...")
    app_pyqt = QApplication(sys.argv)
    
    # --- CARGAR ESTILOS CSS USANDO resource_path ---
    try:
        # Ruta relativa desde la raíz del proyecto hacia el archivo CSS
        stylesheet_relative_path = "styles/styles.css"
        stylesheet_path_resolved = resource_path(stylesheet_relative_path)

        if os.path.exists(stylesheet_path_resolved):
            with open(stylesheet_path_resolved, "r", encoding="utf-8") as f:
                _style = f.read()
                app_pyqt.setStyleSheet(_style)
            print(f"Estilos CSS cargados exitosamente desde: {stylesheet_path_resolved}")
        else:
            print(f"ADVERTENCIA: Archivo de estilos no encontrado en la ruta resuelta: {stylesheet_path_resolved}")
            print(f"             (Ruta relativa original intentada: {stylesheet_relative_path})")
            print("             La aplicación continuará con los estilos por defecto de PyQt.")
    except Exception as e:
        print(f"Error al cargar o aplicar estilos CSS: {e}")
    # --- FIN CARGAR ESTILOS CSS ---

    # Importar LoginView aquí, después de crear QApplication
    from app.views.login_view import LoginView
    
    login_dialog = LoginView()
    print("Mostrando diálogo de inicio de sesión...")
    
    login_result = login_dialog.exec_() # .exec_() es bloqueante

    if login_result == QDialog.Accepted:
        print("Login aceptado. Iniciando ventana principal...")
        # Importar MainWindow aquí para evitar importaciones circulares y asegurar que QApplication existe
        from app.views.main_window import MainWindow
        
        if hasattr(login_dialog, 'user_logged_in_data') and login_dialog.user_logged_in_data:
            user_data_for_main_window = login_dialog.user_logged_in_data
            
            main_app_window = MainWindow(user_data_for_main_window)
            main_app_window.show()
            
            print("Ventana principal mostrada. Entrando al bucle de eventos de PyQt.")
            exit_code = app_pyqt.exec_()
            print(f"Aplicación PyQt terminada con código: {exit_code}")
            sys.exit(exit_code)
        else:
            print("Error crítico: Login fue aceptado pero no se pudieron recuperar los datos del usuario. Saliendo.")
            sys.exit(1) # Salir con código de error
    else:
        print("Login cancelado o diálogo cerrado. Saliendo de la aplicación.")
        sys.exit(0) # Salida normal si el usuario cancela el login