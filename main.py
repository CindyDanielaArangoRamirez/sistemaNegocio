import sys
import threading
from PyQt5.QtWidgets import QApplication
from database.db_connection import initialize_database  # Importar la función
import uvicorn
from api.main import app as fastapi_app


def run_api():
    """Ejecutar la API FastAPI en segundo plano"""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Inicializar la base de datos primero
    initialize_database()  # Esta línea es crucial
    
    # Iniciar API en segundo plano
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True
    api_thread.start()
    
    # Iniciar aplicación principal PyQt
    app = QApplication(sys.argv)
    
    # Cargar estilos CSS
    with open('styles/styles.css', 'r') as f:
        app.setStyleSheet(f.read())
    
    from app.views.login_view import LoginView
    login = LoginView()
    
    if login.exec_() == LoginView.Accepted:
        from app.views.main_window import MainWindow
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())