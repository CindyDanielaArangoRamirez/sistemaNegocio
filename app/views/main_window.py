# app/views/main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QStackedWidget, QLabel, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
# from PyQt5.QtGui import QIcon, QPixmap

from .sales_view import SalesView
from .products_view import ProductsView
from .history_view import HistoryView
from .login_view import LoginView
from PyQt5.QtWidgets import QApplication

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.current_user_data = user_data
        username_display = "N/A"
        if self.current_user_data:
            try:
                username_display = self.current_user_data['username']
            except (KeyError, TypeError, IndexError):
                try:
                    username_display = self.current_user_data[1]
                except (IndexError, TypeError):
                    print("Advertencia (MainWindow): No se pudo obtener 'username' de user_data.")
        
        self.setWindowTitle(f"Sistema de Ferretería - Usuario: {username_display}")
        self.showMaximized()
        self.setup_ui()

    def setup_ui(self):
        self.main_central_widget = QWidget()
        self.setCentralWidget(self.main_central_widget)
        self.main_app_layout = QHBoxLayout(self.main_central_widget)
        self.main_app_layout.setContentsMargins(0, 0, 0, 0)
        self.main_app_layout.setSpacing(0)

        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebar")
        self.sidebar_frame.setFixedWidth(220)
        sidebar_internal_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_internal_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_internal_layout.setSpacing(8)
        sidebar_internal_layout.setAlignment(Qt.AlignTop)

        logo_text_label = QLabel("Ferretería XYZ")
        logo_text_label.setObjectName("sidebarTitle")
        logo_text_label.setAlignment(Qt.AlignCenter)
        logo_text_label.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; padding-bottom: 15px; border-bottom: 1px solid #34495e;")
        sidebar_internal_layout.addWidget(logo_text_label)

        self.sales_button = self.create_sidebar_button("📈 Realizar Venta")
        self.products_button = self.create_sidebar_button("📦 Productos")
        self.history_button = self.create_sidebar_button("📋 Historial Ventas")
        
        sidebar_internal_layout.addWidget(self.sales_button)
        sidebar_internal_layout.addWidget(self.products_button)
        sidebar_internal_layout.addWidget(self.history_button)
        sidebar_internal_layout.addStretch(1)
        self.logout_button = self.create_sidebar_button("🚪 Cerrar Sesión", is_logout_button=True)
        sidebar_internal_layout.addWidget(self.logout_button)
        self.main_app_layout.addWidget(self.sidebar_frame)

        self.content_display_area = QStackedWidget()
        self.content_display_area.setObjectName("contentArea")

        self.sales_view_instance = SalesView(self.current_user_data)
        self.products_view_instance = ProductsView()
        self.history_view_instance = HistoryView()

        self.content_display_area.addWidget(self.sales_view_instance)    # Index 0
        self.content_display_area.addWidget(self.products_view_instance) # Index 1
        self.content_display_area.addWidget(self.history_view_instance)  # Index 2
        
        self.main_app_layout.addWidget(self.content_display_area, 1)

        self.sales_button.clicked.connect(lambda: self.switch_view(0, self.sales_button))
        self.products_button.clicked.connect(lambda: self.switch_view(1, self.products_button))
        self.history_button.clicked.connect(lambda: self.switch_view(2, self.history_button))
        self.logout_button.clicked.connect(self.handle_logout)

        self.switch_view(0, self.sales_button)

    def create_sidebar_button(self, text, is_logout_button=False):
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setObjectName("sidebarButton")
        if is_logout_button:
            button.setStyleSheet("""
                QPushButton#sidebarButton {
                    background-color: #c0392b; color: white; border: none;
                    padding: 12px; text-align: left; padding-left: 20px; font-size: 10pt;
                } QPushButton#sidebarButton:hover { background-color: #e74c3c; }""")
        else:
            button.setStyleSheet("""
                QPushButton#sidebarButton {
                    background-color: transparent; color: #ecf0f1; border: none;
                    padding: 12px; text-align: left; padding-left: 20px; font-size: 10pt;
                }
                QPushButton#sidebarButton:hover { background-color: #34495e; }
                QPushButton#sidebarButton[selected="true"] {
                    background-color: #2980b9; border-left: 3px solid #3498db;
                }""")
        return button

    def switch_view(self, index, clicked_button):
        """Cambia la vista en el QStackedWidget, actualiza el estilo del botón activo,
           y refresca los datos de la vista que se va a mostrar si es necesario."""
        
        # --- LÓGICA DE REFRESCO AÑADIDA AQUÍ ---
        if index == 0: # SalesView (Índice 0)
            if hasattr(self, 'sales_view_instance') and self.sales_view_instance:
                print("MainWindow: Refrescando productos para SalesView...")
                self.sales_view_instance.load_products_for_autocompleter_and_cache()
                self.sales_view_instance.display_low_stock_warning() # También refrescar aviso

        elif index == 1: # ProductsView (Índice 1)
            if hasattr(self, 'products_view_instance') and self.products_view_instance:
                print("MainWindow: Refrescando tabla de productos en ProductsView...")
                self.products_view_instance.load_products_and_setup_completer() # Este método debe recargar todo

        elif index == 2: # HistoryView (Índice 2)
            if hasattr(self, 'history_view_instance') and self.history_view_instance:
                print("MainWindow: Refrescando historial de ventas en HistoryView...")
                if hasattr(self.history_view_instance, 'all_history_data_cache'): # Verificar si el cache existe
                    self.history_view_instance.all_history_data_cache.clear()
                self.history_view_instance.load_and_display_history()
        # --- FIN LÓGICA DE REFRESCO ---
        
        self.content_display_area.setCurrentIndex(index) # Cambiar la vista actual
        
        # Actualizar estilos de los botones del sidebar
        all_sidebar_buttons = [self.sales_button, self.products_button, self.history_button]
        for btn in all_sidebar_buttons:
            is_selected = (btn == clicked_button)
            btn.setProperty("selected", is_selected) # True o False
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            # btn.update() # update() es menos común aquí, polish/unpolish suele ser suficiente

    def handle_logout(self):
        reply = QMessageBox.question(self, "Cerrar Sesión",
                                     "¿Está seguro de que desea cerrar la sesión?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            QApplication.instance().quit()