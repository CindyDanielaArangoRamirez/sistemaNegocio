from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFrame, QStackedWidget, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt
from app.views.sales_view import SalesView
from app.views.products_view import ProductsView
from app.views.history_view import HistoryView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Ferretería")
        self.setGeometry(100, 100, 1024, 768)
        self.setup_ui()
    
    def setup_ui(self):
        # Layout principal
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar.setLayout(sidebar_layout)
        
        # Logo o título
        logo = QLabel("Ferretería XYZ")
        logo.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            qproperty-alignment: AlignCenter;
            border-bottom: 1px solid #2c3e50;
        """)
        
        # Botones del sidebar
        self.sales_btn = self.create_sidebar_button("Realizar Venta")
        self.products_btn = self.create_sidebar_button("Productos")
        self.history_btn = self.create_sidebar_button("Historial")
        
        # Espaciador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Botón de salir
        self.logout_btn = self.create_sidebar_button("Cerrar Sesión", is_logout=True)
        
        # Agregar al sidebar
        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(self.sales_btn)
        sidebar_layout.addWidget(self.products_btn)
        sidebar_layout.addWidget(self.history_btn)
        sidebar_layout.addWidget(spacer)
        sidebar_layout.addWidget(self.logout_btn)
        
        # Área de contenido
        self.content_area = QStackedWidget()
        
        # Crear vistas
        self.sales_view = SalesView()
        self.products_view = ProductsView()
        self.history_view = HistoryView()
        
        # Agregar vistas
        self.content_area.addWidget(self.sales_view)
        self.content_area.addWidget(self.products_view)
        self.content_area.addWidget(self.history_view)
        
        # Conectar botones
        self.sales_btn.clicked.connect(lambda: self.change_view(0))
        self.products_btn.clicked.connect(lambda: self.change_view(1))
        self.history_btn.clicked.connect(lambda: self.change_view(2))
        self.logout_btn.clicked.connect(self.close)
        
        # Agregar al layout principal
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)
        
        # Mostrar vista inicial
        self.change_view(0)
    
    def create_sidebar_button(self, text, is_logout=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        
        if is_logout:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 12px;
                    border: none;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    padding: 12px;
                    border: none;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #2c3e50;
                }
            """)
        
        return btn
    
    def change_view(self, index):
        self.content_area.setCurrentIndex(index)
        
        # Actualizar estilos de botones activos
        buttons = [self.sales_btn, self.products_btn, self.history_btn]
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 12px;
                        border: none;
                        text-align: left;
                        padding-left: 20px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: white;
                        padding: 12px;
                        border: none;
                        text-align: left;
                        padding-left: 20px;
                    }
                    QPushButton:hover {
                        background-color: #2c3e50;
                    }
                """)