from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QCompleter, 
                             QHeaderView, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QDoubleValidator
from app.models.product_model import ProductModel
from app.models.sale_model import SaleModel
from app.views.dialogs import InvoiceDialog, BaseDialog
from utils.printer import Printer

class SalesView(QWidget):
    def __init__(self):
        super().__init__()
        self.product_model = ProductModel()
        self.sale_model = SaleModel()
        self.printer = Printer()
        self.current_sale_items = []
        self.base_registered = False
        self.base_amount = 0.0
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Sección de base inicial
        self.base_layout = QHBoxLayout()
        self.base_layout.setSpacing(10)
        
        base_label = QLabel("Base Inicial:")
        base_label.setStyleSheet("font-weight: bold;")
        
        self.base_input = QLineEdit()
        self.base_input.setPlaceholderText("Ingrese el monto inicial de caja")
        self.base_input.setValidator(QDoubleValidator(0, 999999, 2))
        self.base_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        
        self.register_base_btn = QPushButton("Registrar Base")
        self.register_base_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.register_base_btn.clicked.connect(self.register_base)
        
        self.base_layout.addWidget(base_label)
        self.base_layout.addWidget(self.base_input)
        self.base_layout.addWidget(self.register_base_btn)
        self.base_layout.addStretch()
        
        # Sección de venta (inicialmente oculta)
        self.sale_section = QWidget()
        self.sale_section.setVisible(False)
        sale_layout = QVBoxLayout()
        sale_layout.setSpacing(15)
        
        # Información de base
        self.base_info = QLabel()
        self.base_info.setStyleSheet("font-weight: bold; color: #27ae60;")
        
        # Buscador de productos
        product_search_layout = QHBoxLayout()
        product_search_layout.setSpacing(10)
        
        product_label = QLabel("Producto:")
        product_label.setStyleSheet("font-weight: bold;")
        
        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("Buscar producto...")
        self.product_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        
        # Autocompletado
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.product_input.setCompleter(self.completer)
        self.product_input.textChanged.connect(self.update_completer)
        
        quantity_label = QLabel("Cantidad:")
        quantity_label.setStyleSheet("font-weight: bold;")
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("1")
        self.quantity_input.setValidator(QDoubleValidator(0.01, 9999, 2))
        self.quantity_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        
        self.add_product_btn = QPushButton("Agregar")
        self.add_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.add_product_btn.clicked.connect(self.add_product_to_sale)
        
        product_search_layout.addWidget(product_label)
        product_search_layout.addWidget(self.product_input)
        product_search_layout.addWidget(quantity_label)
        product_search_layout.addWidget(self.quantity_input)
        product_search_layout.addWidget(self.add_product_btn)
        
        # Tabla de productos en venta
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Precio Unitario", "Subtotal"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 5px;
            }
        """)
        
        # Total
        self.total_layout = QHBoxLayout()
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        self.total_layout.addStretch()
        self.total_layout.addWidget(self.total_label)
        
        # Botones finales
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.generate_sale_btn = QPushButton("Generar Venta")
        self.generate_sale_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.generate_sale_btn.clicked.connect(self.generate_sale)
        self.generate_sale_btn.setEnabled(False)
        
        self.clear_sale_btn = QPushButton("Limpiar Venta")
        self.clear_sale_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_sale_btn.clicked.connect(self.clear_sale)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.clear_sale_btn)
        buttons_layout.addWidget(self.generate_sale_btn)
        
        # Agregar al layout de venta
        sale_layout.addWidget(self.base_info)
        sale_layout.addLayout(product_search_layout)
        sale_layout.addWidget(self.products_table)
        sale_layout.addLayout(self.total_layout)
        sale_layout.addLayout(buttons_layout)
        
        self.sale_section.setLayout(sale_layout)
        
        # Agregar al layout principal
        layout.addLayout(self.base_layout)
        layout.addWidget(self.sale_section)
        
        self.setLayout(layout)
    
    def update_completer(self, text):
        """Actualizar el autocompletado según lo que escribe el usuario"""
        if len(text) >= 1:
            products = self.product_model.search_products(text)
            product_names = [product[1] for product in products]
            model = QStringListModel()
            model.setStringList(product_names)
            self.completer.setModel(model)
    
    def register_base(self):
        """Registrar el monto inicial de caja"""
        base_text = self.base_input.text().strip()
        
        if not base_text:
            QMessageBox.warning(self, "Error", "Por favor ingrese un monto válido")
            return
            
        try:
            self.base_amount = float(base_text)
            self.base_registered = True
            
            # Ocultar sección de base y mostrar sección de venta
            self.base_input.setEnabled(False)
            self.register_base_btn.setEnabled(False)
            self.sale_section.setVisible(True)
            self.base_info.setText(f"Base registrada: ${self.base_amount:,.2f}")
            
            QMessageBox.information(self, "Éxito", "Base registrada correctamente. Ya puede comenzar a registrar ventas")
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingrese un monto válido")
    
    def add_product_to_sale(self):
        """Agregar un producto a la venta actual"""
        product_name = self.product_input.text().strip()
        quantity_text = self.quantity_input.text().strip()
        
        if not product_name or not quantity_text:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
            
        try:
            quantity = float(quantity_text)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingrese una cantidad válida")
            return
            
        # Buscar el producto en la base de datos
        products = self.product_model.search_products(product_name)
        if not products:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            return
            
        # Tomar el primer producto que coincida
        product_id, name, stock, price = products[0]
        
        # Verificar stock
        if quantity > stock:
            QMessageBox.warning(self, "Error", f"No hay suficiente stock. Disponible: {stock}")
            return
            
        # Calcular subtotal
        subtotal = quantity * price
        
        # Agregar a la lista de items
        self.current_sale_items.append({
            'id': product_id,
            'name': name,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal
        })
        
        # Actualizar tabla
        self.update_products_table()
        
        # Limpiar inputs
        self.product_input.clear()
        self.quantity_input.clear()
        self.product_input.setFocus()
        
        # Habilitar botón de generar venta si hay items
        self.generate_sale_btn.setEnabled(len(self.current_sale_items) > 0)
    
    def update_products_table(self):
        """Actualizar la tabla de productos con los items actuales"""
        self.products_table.setRowCount(len(self.current_sale_items))
        
        total = 0.0
        
        for row, item in enumerate(self.current_sale_items):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.products_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.products_table.setItem(row, 2, QTableWidgetItem(f"{item['quantity']:,}"))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"${item['price']:,.2f}"))
            self.products_table.setItem(row, 4, QTableWidgetItem(f"${item['subtotal']:,.2f}"))
            
            total += item['subtotal']
        
        self.total_label.setText(f"Total: ${total:,.2f}")
    
    def generate_sale(self):
        """Generar la venta y mostrar diálogo de factura"""
        total = sum(item['subtotal'] for item in self.current_sale_items)
        
        # Mostrar diálogo de factura
        invoice_dialog = InvoiceDialog(self.base_amount, self.current_sale_items, total, self)
        if invoice_dialog.exec_() == InvoiceDialog.Accepted:
            # Registrar la venta en la base de datos
            items_for_db = [
                (item['id'], item['quantity'], item['price'], item['subtotal']) 
                for item in self.current_sale_items
            ]
            
            sale_id = self.sale_model.create_sale(1, self.base_amount, total, items_for_db)
            
            if sale_id:
                # Actualizar stock de productos
                for item in self.current_sale_items:
                    self.product_model.update_stock(item['id'], item['quantity'])
                
                # Imprimir factura si se seleccionó
                if invoice_dialog.print_invoice:
                    customer_payment = invoice_dialog.payment_amount
                    change = invoice_dialog.change_amount
                    self.printer.print_invoice(self.current_sale_items, total, customer_payment, change)
                
                QMessageBox.information(self, "Éxito", "Venta registrada correctamente")
                self.clear_sale()
            else:
                QMessageBox.critical(self, "Error", "Ocurrió un error al registrar la venta")
    
    def clear_sale(self):
        """Limpiar la venta actual"""
        self.current_sale_items = []
        self.products_table.setRowCount(0)
        self.total_label.setText("Total: $0.00")
        self.generate_sale_btn.setEnabled(False)
        self.product_input.setFocus()