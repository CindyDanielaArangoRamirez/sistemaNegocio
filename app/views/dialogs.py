# app/views/dialogs.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QGroupBox, QHeaderView, QFormLayout # QSpacerItem y QSizePolicy no se usan aquí
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

# BaseDialog puede permanecer como está si decides usarlo,
# pero la última SalesView que te di no lo llama.
# Si SalesView usa BaseDialog, entonces BaseDialog debería devolver el monto
# y SalesView lo pasaría a SalesController.set_daily_base.
class BaseDialog(QDialog):
    """Diálogo para registrar la base inicial"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Base Inicial")
        self.setFixedSize(350, 180) # Un poco más de espacio
        self.base_value = 0.0
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self) # Establecer layout en el QDialog
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        info_label = QLabel("Ingrese el monto inicial de caja:")
        info_label.setStyleSheet("font-size: 10pt;")

        self.base_input_lineedit = QLineEdit() # Renombrado para consistencia
        self.base_input_lineedit.setPlaceholderText("Monto en $")
        self.base_input_lineedit.setValidator(QDoubleValidator(0, 9999999.99, 2)) # Rango mayor
        self.base_input_lineedit.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch() # Empujar botones a la derecha
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("secondaryButton") # Para CSS
        self.cancel_button.clicked.connect(self.reject) # reject() cierra con QDialog.Rejected

        self.accept_button = QPushButton("Aceptar")
        self.accept_button.setObjectName("primaryButton") # Para CSS
        self.accept_button.setDefault(True) # Presionar Enter lo activará
        self.accept_button.clicked.connect(self.handle_accept_input)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.accept_button)

        layout.addWidget(info_label)
        layout.addWidget(self.base_input_lineedit)
        layout.addStretch() # Espacio antes de los botones
        layout.addLayout(buttons_layout)
        self.setLayout(layout) # Asegurarse que el layout se establece

    def handle_accept_input(self):
        """Validar el input antes de aceptar"""
        base_text = self.base_input_lineedit.text().strip().replace(",",".")
        if base_text:
            try:
                self.base_value = float(base_text)
                if self.base_value < 0:
                    QMessageBox.warning(self, "Monto Inválido", "El monto de la base no puede ser negativo.")
                    return
                self.accept() # Cierra con QDialog.Accepted
            except ValueError:
                QMessageBox.warning(self, "Error de Formato", "Por favor ingrese un monto numérico válido.")
        else:
            QMessageBox.warning(self, "Campo Vacío", "Por favor ingrese un monto para la base.")

    def get_base_amount(self):
        """Devuelve el monto de la base ingresado."""
        return self.base_value


class InvoiceDialog(QDialog):
    """Diálogo para confirmar la venta, ingresar pago y generar factura"""
    def __init__(self, items_in_sale, total_sale_amount, parent=None): # base_amount ya no es necesario aquí si SalesController lo maneja
        super().__init__(parent)
        # self.base_amount_from_sale = base_amount # Ya no se necesita si SalesController tiene la base
        self.items_for_invoice = items_in_sale # Debería ser [{name, quantity_sold, price_per_unit, subtotal}, ...]
        self.total_sale_amount = total_sale_amount
        
        self.user_wants_to_print_invoice = False
        self.customer_payment_amount = 0.0 # Monto con el que paga el cliente
        self.change_to_give_amount = 0.0   # Cambio a entregar

        self.setWindowTitle("Confirmar Venta y Factura")
        self.setMinimumSize(550, 450) # Ajustar tamaño según contenido
        self.setup_invoice_ui()

    def setup_invoice_ui(self):
        main_layout = QVBoxLayout(self) # Layout principal del diálogo
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # --- Grupo: Detalle de la Venta (Tabla de Productos) ---
        products_details_groupbox = QGroupBox("Detalle de la Venta")
        products_details_layout = QVBoxLayout()

        self.invoice_products_tablewidget = QTableWidget()
        self.invoice_products_tablewidget.setColumnCount(4) # Producto, Cant., P. Unit., Subtotal
        self.invoice_products_tablewidget.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal"])
        header = self.invoice_products_tablewidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch) # Nombre del Producto
        for i in range(1, 4): # Cantidad, P.Unit, Subtotal
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.invoice_products_tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.invoice_products_tablewidget.setAlternatingRowColors(True)
        
        # Llenar tabla con items
        self.invoice_products_tablewidget.setRowCount(len(self.items_for_invoice))
        for row_idx, item_data in enumerate(self.items_for_invoice):
            self.invoice_products_tablewidget.setItem(row_idx, 0, QTableWidgetItem(item_data.get('name', 'N/A')))
            # Asegúrate que 'quantity_sold' y 'price_per_unit' son los nombres correctos de las claves
            self.invoice_products_tablewidget.setItem(row_idx, 1, QTableWidgetItem(str(item_data.get('quantity_sold', 0))))
            self.invoice_products_tablewidget.setItem(row_idx, 2, QTableWidgetItem(f"${item_data.get('price_per_unit', 0.0):,.2f}"))
            self.invoice_products_tablewidget.setItem(row_idx, 3, QTableWidgetItem(f"${item_data.get('subtotal', 0.0):,.2f}"))
        
        products_details_layout.addWidget(self.invoice_products_tablewidget)
        products_details_groupbox.setLayout(products_details_layout)
        main_layout.addWidget(products_details_groupbox)

        # --- Grupo: Totales y Pago ---
        payment_summary_groupbox = QGroupBox("Resumen y Pago")
        payment_summary_form_layout = QFormLayout() # Usar QFormLayout para pares etiqueta-input
        payment_summary_form_layout.setSpacing(8)

        self.total_sale_display_label = QLabel(f"${self.total_sale_amount:,.2f}")
        self.total_sale_display_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2c3e50;")
        payment_summary_form_layout.addRow("Total Venta:", self.total_sale_display_label)
        
        self.customer_payment_lineedit = QLineEdit()
        self.customer_payment_lineedit.setPlaceholderText("Monto recibido del cliente")
        self.customer_payment_lineedit.setValidator(QDoubleValidator(0, 9999999.99, 2))
        self.customer_payment_lineedit.textChanged.connect(self.handle_calculate_change)
        self.customer_payment_lineedit.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        payment_summary_form_layout.addRow("Cliente Paga con ($):", self.customer_payment_lineedit)

        self.change_due_display_label = QLabel("$0.00")
        self.change_due_display_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        payment_summary_form_layout.addRow("Cambio a Entregar:", self.change_due_display_label)

        payment_summary_groupbox.setLayout(payment_summary_form_layout)
        main_layout.addWidget(payment_summary_groupbox)
        
        # --- Botones de Acción ---
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.addStretch()

        self.cancel_button = QPushButton("Cancelar Venta")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.clicked.connect(self.reject) # Cierra y devuelve QDialog.Rejected
        action_buttons_layout.addWidget(self.cancel_button)
        
        self.confirm_and_print_button = QPushButton("✅ Confirmar y Imprimir Factura")
        self.confirm_and_print_button.setObjectName("ctaButton") # Estilo de "Call to Action"
        self.confirm_and_print_button.setEnabled(False) # Habilitar cuando el pago sea suficiente
        self.confirm_and_print_button.clicked.connect(self.handle_accept_and_print)
        action_buttons_layout.addWidget(self.confirm_and_print_button)
        
        self.confirm_only_button = QPushButton("✔️ Confirmar Venta (Sin Imprimir)")
        self.confirm_only_button.setObjectName("primaryButton")
        self.confirm_only_button.setEnabled(False) # Habilitar cuando el pago sea suficiente
        self.confirm_only_button.clicked.connect(self.handle_accept_without_printing)
        action_buttons_layout.addWidget(self.confirm_only_button)
        
        main_layout.addLayout(action_buttons_layout)
        self.setLayout(main_layout) # Establecer layout principal del diálogo
        self.customer_payment_lineedit.setFocus() # Poner foco en el input de pago

    def handle_calculate_change(self):
        """Calcula el cambio cuando el cliente ingresa el monto de pago."""
        try:
            payment_text = self.customer_payment_lineedit.text().strip().replace(",",".")
            self.customer_payment_amount = float(payment_text) if payment_text else 0.0
            
            can_proceed = self.customer_payment_amount >= self.total_sale_amount
            self.confirm_and_print_button.setEnabled(can_proceed)
            self.confirm_only_button.setEnabled(can_proceed)

            if can_proceed:
                self.change_to_give_amount = self.customer_payment_amount - self.total_sale_amount
                self.change_due_display_label.setText(f"${self.change_to_give_amount:,.2f}")
                self.change_due_display_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: green;")
            else:
                amount_needed = self.total_sale_amount - self.customer_payment_amount
                self.change_due_display_label.setText(f"Faltan: ${amount_needed:,.2f}")
                self.change_due_display_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: red;")
                self.change_to_give_amount = 0.0 # Resetear cambio si el pago es insuficiente
        except ValueError:
            self.change_due_display_label.setText("Monto inválido")
            self.change_due_display_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: red;")
            self.confirm_and_print_button.setEnabled(False)
            self.confirm_only_button.setEnabled(False)
            self.customer_payment_amount = 0.0
            self.change_to_give_amount = 0.0


    def handle_accept_and_print(self):
        """Aceptar la venta y marcar para imprimir factura."""
        if self.customer_payment_amount < self.total_sale_amount:
            QMessageBox.warning(self, "Pago Insuficiente", "El monto pagado no cubre el total de la venta.")
            return
        self.user_wants_to_print_invoice = True
        self.accept() # Cierra el diálogo con QDialog.Accepted

    def handle_accept_without_printing(self):
        """Aceptar la venta sin marcar para imprimir factura."""
        if self.customer_payment_amount < self.total_sale_amount:
            QMessageBox.warning(self, "Pago Insuficiente", "El monto pagado no cubre el total de la venta.")
            return
        self.user_wants_to_print_invoice = False
        self.accept() # Cierra el diálogo con QDialog.Accepted

    # Métodos para que SalesView obtenga los resultados del diálogo
    def get_dialog_results(self):
        return {
            "print_invoice": self.user_wants_to_print_invoice,
            "customer_payment": self.customer_payment_amount,
            "change_given": self.change_to_give_amount
        }