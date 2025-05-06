from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QInputDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from app.controllers.products_controller import ProductsController

class ProductsView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ProductsController()
        self.selected_product_id = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar producto...")
        self.search_input.textChanged.connect(self.search_products)
        
        self.add_btn = QPushButton("Agregar Producto")
        self.add_btn.clicked.connect(self.show_add_dialog)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.add_btn)

        # Tabla de productos
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad", "Precio"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.clicked.connect(self.select_product)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Editar")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.show_edit_dialog)
        
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_product)
        
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()

        layout.addLayout(search_layout)
        layout.addWidget(self.products_table)
        layout.addLayout(action_layout)

        self.setLayout(layout)
        self.load_products()

    def load_products(self, search_term=None):
        """Cargar productos en la tabla"""
        if search_term:
            products = self.controller.search_products(search_term)
        else:
            products = self.controller.search_products("")  # Todos los productos
        
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.products_table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(product[2])))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"${product[3]:,.2f}"))

    def search_products(self):
        """Buscar productos según el texto ingresado"""
        search_term = self.search_input.text().strip()
        self.load_products(search_term)

    def select_product(self, index):
        """Seleccionar un producto de la tabla"""
        self.selected_product_id = int(self.products_table.item(index.row(), 0).text())
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def show_add_dialog(self):
        """Mostrar diálogo para agregar producto"""
        name, ok = QInputDialog.getText(self, "Agregar Producto", "Nombre del producto:")
        if ok and name:
            quantity, ok = QInputDialog.getDouble(
                self, "Agregar Producto", "Cantidad disponible:", 
                min=0.01, decimals=2
            )
            if ok:
                price, ok = QInputDialog.getDouble(
                    self, "Agregar Producto", "Precio unitario:", 
                    min=0.01, decimals=2
                )
                if ok and self.controller.add_product(name, quantity, price):
                    self.load_products()

    def show_edit_dialog(self):
        """Mostrar diálogo para editar producto"""
        if not self.selected_product_id:
            return
            
        # Obtener datos actuales del producto
        products = self.controller.search_products("")
        product = next((p for p in products if p[0] == self.selected_product_id), None)
        
        if product:
            name, ok = QInputDialog.getText(
                self, "Editar Producto", "Nombre:", 
                text=product[1]
            )
            if ok and name:
                quantity, ok = QInputDialog.getDouble(
                    self, "Editar Producto", "Cantidad:", 
                    value=product[2], min=0.01, decimals=2
                )
                if ok:
                    price, ok = QInputDialog.getDouble(
                        self, "Editar Producto", "Precio:", 
                        value=product[3], min=0.01, decimals=2
                    )
                    if ok and self.controller.update_product(
                        self.selected_product_id, name, quantity, price
                    ):
                        self.load_products()

    def delete_product(self):
        """Eliminar el producto seleccionado"""
        if self.selected_product_id:
            confirm = QMessageBox.question(
                self, "Confirmar", 
                "¿Está seguro de eliminar este producto?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                if self.controller.delete_product(self.selected_product_id):
                    self.load_products()
                    self.selected_product_id = None
                    self.edit_btn.setEnabled(False)
                    self.delete_btn.setEnabled(False)