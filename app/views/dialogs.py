from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QSpacerItem, 
                             QSizePolicy, QGroupBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

class BaseDialog(QDialog):
    """Diálogo para registrar la base inicial"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Base Inicial")
        self.setFixedSize(300, 150)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        info_label = QLabel("Ingrese el monto inicial de caja:")
        
        self.base_input = QLineEdit()
        self.base_input.setPlaceholderText("Monto en $")
        self.base_input.setValidator(QDoubleValidator(0, 999999, 2))
        
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        accept_btn = QPushButton("Aceptar")
        accept_btn.clicked.connect(self.accept_input)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(accept_btn)
        
        layout.addWidget(info_label)
        layout.addWidget(self.base_input)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def accept_input(self):
        """Validar el input antes de aceptar"""
        if self.base_input.text().strip():
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Por favor ingrese un monto válido")

class InvoiceDialog(QDialog):
    """Diálogo para confirmar la venta y generar factura"""
    def __init__(self, base_amount, items, total, parent=None):
        super().__init__(parent)
        self.base_amount = base_amount
        self.items = items
        self.total = total
        self.print_invoice = False
        self.payment_amount = 0
        self.change_amount = 0
        self.setWindowTitle("Confirmar Venta")
        self.setMinimumSize(500, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tabla de productos
        products_group = QGroupBox("Detalle de la Venta")
        products_layout = QVBoxLayout()
        
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Producto", "Cant.", "P. Unit.", "Subtotal"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Llenar tabla
        self.products_table.setRowCount(len(self.items))
        for row, item in enumerate(self.items):
            self.products_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.products_table.setItem(row, 1, QTableWidgetItem(f"{item['quantity']:,}"))
            self.products_table.setItem(row, 2, QTableWidgetItem(f"${item['price']:,.2f}"))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"${item['subtotal']:,.2f}"))
        
        products_layout.addWidget(self.products_table)
        products_group.setLayout(products_layout)
        
        # Totales
        totals_group = QGroupBox("Totales")
        totals_layout = QVBoxLayout()
        
        self.base_label = QLabel(f"Base inicial: ${self.base_amount:,.2f}")
        self.total_label = QLabel(f"Total venta: ${self.total:,.2f}")
        
        # Pago del cliente
        payment_layout = QHBoxLayout()
        payment_label = QLabel("Pago con:")
        
        self.payment_input = QLineEdit()
        self.payment_input.setValidator(QDoubleValidator(0, 999999, 2))
        self.payment_input.textChanged.connect(self.calculate_change)
        
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.payment_input)
        
        # Cambio
        self.change_label = QLabel("Cambio: $0.00")
        
        totals_layout.addWidget(self.base_label)
        totals_layout.addWidget(self.total_label)
        totals_layout.addLayout(payment_layout)
        totals_layout.addWidget(self.change_label)
        totals_group.setLayout(totals_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        print_btn = QPushButton("Imprimir Factura")
        print_btn.clicked.connect(self.accept_and_print)
        
        accept_btn = QPushButton("Aceptar sin Imprimir")
        accept_btn.clicked.connect(self.accept_without_print)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(print_btn)
        buttons_layout.addWidget(accept_btn)
        
        # Agregar al layout principal
        layout.addWidget(products_group)
        layout.addWidget(totals_group)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def calculate_change(self):
        """Calcular el cambio cuando el cliente ingresa el pago"""
        try:
            payment = float(self.payment_input.text())
            change = payment - self.total
            if change >= 0:
                self.change_label.setText(f"Cambio: ${change:,.2f}")
                self.change_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.change_label.setText(f"Faltan: ${-change:,.2f}")
                self.change_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        except ValueError:
            self.change_label.setText("Cambio: $0.00")
            self.change_label.setStyleSheet("")
    
    def accept_and_print(self):
        """Aceptar la venta e imprimir factura"""
        try:
            payment = float(self.payment_input.text())
            if payment < self.total:
                QMessageBox.warning(self, "Error", "El pago no cubre el total de la venta")
                return
                
            self.payment_amount = payment
            self.change_amount = payment - self.total
            self.print_invoice = True
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese un monto de pago válido")
    
    def accept_without_print(self):
        """Aceptar la venta sin imprimir factura"""
        self.print_invoice = False
        self.accept()