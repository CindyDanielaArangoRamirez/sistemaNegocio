# app/views/products_view.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QFrame,
    QCompleter # <--- IMPORTACIÓN IMPORTANTE
)
from PyQt5.QtCore import Qt, QStringListModel # QStringListModel para el QCompleter

from app.controllers.products_controller import ProductsController
# ProductFormDialog debería estar aquí o importado si está en dialogs.py
# class ProductFormDialog(QDialog): ... (como lo teníamos antes)

# --- Diálogo Personalizado para Agregar/Editar Productos (Incluido aquí por completitud) ---
# Si lo tienes en dialogs.py, solo necesitas importarlo.
class ProductFormDialog(QDialog):
    def __init__(self, product_data_to_edit=None, parent=None):
        super().__init__(parent)
        self.product_data_to_edit = product_data_to_edit

        if self.product_data_to_edit:
            self.setWindowTitle("Editar Producto")
        else:
            self.setWindowTitle("Agregar Nuevo Producto")
        
        self.setMinimumWidth(400)
        self.init_form_ui()
        if self.product_data_to_edit:
            self.populate_form_for_edit()

    def init_form_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_lineedit = QLineEdit()
        self.name_lineedit.setPlaceholderText("Ej: Martillo de Uña")
        form_layout.addRow("Nombre del Producto:", self.name_lineedit)

        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(0, 99999)
        self.quantity_spinbox.setSuffix(" unidades")
        form_layout.addRow("Cantidad Disponible:", self.quantity_spinbox)

        self.purchase_price_spinbox = QDoubleSpinBox()
        self.purchase_price_spinbox.setRange(0.00, 999999.99)
        self.purchase_price_spinbox.setDecimals(2)
        self.purchase_price_spinbox.setPrefix("$ ")
        form_layout.addRow("Precio de Compra:", self.purchase_price_spinbox)

        self.sale_price_spinbox = QDoubleSpinBox()
        self.sale_price_spinbox.setRange(0.00, 999999.99)
        self.sale_price_spinbox.setDecimals(2)
        self.sale_price_spinbox.setPrefix("$ ")
        form_layout.addRow("Precio de Venta:", self.sale_price_spinbox)
        
        layout.addLayout(form_layout)

        button_box_layout = QHBoxLayout()
        self.ok_button = QPushButton("Aceptar")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.on_accept_data)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_box_layout.addStretch()
        button_box_layout.addWidget(self.cancel_button)
        button_box_layout.addWidget(self.ok_button)
        layout.addLayout(button_box_layout)

    def populate_form_for_edit(self):
        if self.product_data_to_edit:
            self.name_lineedit.setText(self.product_data_to_edit['name'])
            self.quantity_spinbox.setValue(self.product_data_to_edit['quantity_available'])
            self.purchase_price_spinbox.setValue(self.product_data_to_edit['purchase_price'])
            self.sale_price_spinbox.setValue(self.product_data_to_edit['sale_price'])

    def get_data(self):
        name = self.name_lineedit.text().strip()
        if not name:
            QMessageBox.warning(self, "Dato Faltante", "El nombre del producto no puede estar vacío.")
            return None
        return {
            'name': name,
            'quantity_available': self.quantity_spinbox.value(),
            'purchase_price': self.purchase_price_spinbox.value(),
            'sale_price': self.sale_price_spinbox.value(),
        }

    def on_accept_data(self):
        if self.get_data() is not None:
            self.accept()
# --- Fin ProductFormDialog ---


class ProductsView(QWidget):
    def __init__(self):
        super().__init__()
        self.current_selected_product_id = None
        self.all_product_names_cache = [] # Cache de nombres para el completer
        self.setup_ui()
        self.load_products_and_setup_completer() # Carga inicial y configuración del completer

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_bar_layout = QHBoxLayout()
        title_label = QLabel("Gestión de Productos")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        self.add_product_button = QPushButton("➕ Agregar Producto")
        self.add_product_button.setStyleSheet("padding: 7px 10px; font-size: 10pt;")
        self.add_product_button.clicked.connect(self.open_add_product_dialog)
        title_bar_layout.addWidget(self.add_product_button)
        layout.addLayout(title_bar_layout)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input_lineedit = QLineEdit()
        self.search_input_lineedit.setPlaceholderText("Buscar producto por nombre...")
        
        # Configuración del QCompleter para la búsqueda
        self.products_view_completer = QCompleter(self)
        self.products_view_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.products_view_completer.setFilterMode(Qt.MatchStartsWith) # Coincidir al inicio
        self.search_input_lineedit.setCompleter(self.products_view_completer)
        
        self.search_input_lineedit.textChanged.connect(self.filter_products_by_name_in_table) # Filtra la tabla en tiempo real
        search_layout.addWidget(self.search_input_lineedit)
        layout.addLayout(search_layout)

        self.low_stock_warning_frame = QFrame()
        self.low_stock_warning_frame.setObjectName("lowStockWarning")
        low_stock_layout = QHBoxLayout(self.low_stock_warning_frame)
        self.low_stock_label = QLabel("")
        low_stock_layout.addWidget(self.low_stock_label, 1)
        close_warning_button = QPushButton("✕")
        close_warning_button.setObjectName("closeWarningButton")
        close_warning_button.setFixedSize(20, 20)
        close_warning_button.clicked.connect(self.low_stock_warning_frame.hide)
        low_stock_layout.addWidget(close_warning_button)
        self.low_stock_warning_frame.hide()
        self.low_stock_warning_frame.setStyleSheet("""
            QFrame#lowStockWarning { background-color: #fcf8e3; border: 1px solid #faebcc; border-radius: 4px; padding: 8px; margin-top: 5px; margin-bottom: 10px; }
            QFrame#lowStockWarning QLabel { color: #8a6d3b; background-color: transparent; border: none; }
            QPushButton#closeWarningButton { background-color: transparent; border: none; color: #8a6d3b; font-weight: bold; font-size: 10pt;}
            QPushButton#closeWarningButton:hover { color: #66512c; }
        """)
        layout.addWidget(self.low_stock_warning_frame)

        self.products_tablewidget = QTableWidget()
        self.products_tablewidget.setColumnCount(6)
        self.products_tablewidget.setHorizontalHeaderLabels(["ID", "Nombre Producto", "Cant. Disp.", "Precio Compra", "Precio Venta", "Estado"])
        header = self.products_tablewidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        for i in [0, 2, 5]: header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.products_tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_tablewidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_tablewidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.products_tablewidget.itemSelectionChanged.connect(self.on_product_selection_changed)
        layout.addWidget(self.products_tablewidget)

        action_buttons_layout = QHBoxLayout()
        self.edit_product_button = QPushButton("✏️ Editar")
        self.edit_product_button.setEnabled(False)
        self.edit_product_button.clicked.connect(self.open_edit_product_dialog)
        action_buttons_layout.addWidget(self.edit_product_button)
        self.delete_restore_button = QPushButton("🗑️ Desactivar")
        self.delete_restore_button.setEnabled(False)
        self.delete_restore_button.clicked.connect(self.handle_delete_restore_product)
        action_buttons_layout.addWidget(self.delete_restore_button)
        action_buttons_layout.addStretch()
        layout.addLayout(action_buttons_layout)
        self.setLayout(layout)

    def update_completer_model(self):
        """Actualiza el modelo de datos para el QCompleter."""
        # Obtener todos los nombres de productos (activos e inactivos) para las sugerencias de búsqueda
        all_products_for_completer = ProductsController.get_all_products_for_management_view()
        self.all_product_names_cache = [p['name'] for p in all_products_for_completer] if all_products_for_completer else []
        
        completer_model = QStringListModel(self.all_product_names_cache)
        self.products_view_completer.setModel(completer_model)

    def load_products_and_setup_completer(self, search_term=None):
        """Carga productos en la tabla y actualiza el modelo del completer."""
        self.products_tablewidget.setRowCount(0)
        
        if search_term:
            products_data = ProductsController.search_products_for_management_view(search_term)
        else:
            products_data = ProductsController.get_all_products_for_management_view()

        if not products_data:
            self.update_completer_model() # Actualizar completer incluso si la tabla está vacía (para que sepa todos los nombres)
            self.check_and_display_low_stock()
            return

        for row_index, product_row in enumerate(products_data):
            self.products_tablewidget.insertRow(row_index)
            self.products_tablewidget.setItem(row_index, 0, QTableWidgetItem(str(product_row['id'])))
            self.products_tablewidget.setItem(row_index, 1, QTableWidgetItem(product_row['name']))
            self.products_tablewidget.setItem(row_index, 2, QTableWidgetItem(str(product_row['quantity_available'])))
            self.products_tablewidget.setItem(row_index, 3, QTableWidgetItem(f"${product_row['purchase_price']:.2f}"))
            self.products_tablewidget.setItem(row_index, 4, QTableWidgetItem(f"${product_row['sale_price']:.2f}"))
            status_text = "Activo" if product_row['is_active'] else "Inactivo"
            status_item = QTableWidgetItem(status_text)
            self.products_tablewidget.setItem(row_index, 5, status_item)

        self.current_selected_product_id = None
        self.edit_product_button.setEnabled(False)
        self.delete_restore_button.setEnabled(False)
        self.delete_restore_button.setText("🗑️ Desactivar")
        
        self.update_completer_model() # Actualizar el modelo del QCompleter
        self.check_and_display_low_stock()

    def filter_products_by_name_in_table(self): # Renombrado para claridad
        """Filtra los productos en la tabla según el texto de búsqueda."""
        search_term = self.search_input_lineedit.text().strip()
        # No necesitamos actualizar el completer aquí, solo la tabla.
        # El completer se actualiza cuando se cargan todos los productos.
        self.load_products_and_setup_completer(search_term=search_term)


    def check_and_display_low_stock(self, threshold=5):
        low_stock_products = ProductsController.get_low_stock_products_for_alert(threshold=threshold)
        if low_stock_products:
            product_names = [p['name'] for p in low_stock_products]
            alert_message = f"⚠️ Stock Bajo: {', '.join(product_names)}"
            if len(alert_message) > 100: alert_message = alert_message[:97] + "..."
            self.low_stock_label.setText(alert_message)
            self.low_stock_warning_frame.show()
        else:
            self.low_stock_warning_frame.hide()
            
    def on_product_selection_changed(self):
        selected_items = self.products_tablewidget.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            self.current_selected_product_id = int(self.products_tablewidget.item(selected_row, 0).text())
            product_status_text = self.products_tablewidget.item(selected_row, 5).text()
            is_currently_active = (product_status_text == "Activo")
            self.edit_product_button.setEnabled(True)
            self.delete_restore_button.setEnabled(True)
            if is_currently_active:
                self.delete_restore_button.setText("🗑️ Desactivar")
            else:
                self.delete_restore_button.setText("🔄 Restaurar")
        else:
            self.current_selected_product_id = None
            self.edit_product_button.setEnabled(False)
            self.delete_restore_button.setEnabled(False)
            self.delete_restore_button.setText("🗑️ Desactivar")

    def open_add_product_dialog(self):
        dialog = ProductFormDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                product_id = ProductsController.add_new_product(
                    name=data['name'], quantity_available=data['quantity_available'],
                    sale_price=data['sale_price'], purchase_price=data['purchase_price']
                )
                if product_id:
                    QMessageBox.information(self, "Éxito", f"Producto '{data['name']}' agregado.")
                    self.load_products_and_setup_completer() # Recargar y actualizar completer
                else:
                    QMessageBox.warning(self, "Error", "No se pudo agregar el producto.")

    def open_edit_product_dialog(self):
        if not self.current_selected_product_id:
            QMessageBox.warning(self, "Sin Selección", "Seleccione un producto para editar.")
            return
        product_to_edit = ProductsController.get_product_details(self.current_selected_product_id)
        if not product_to_edit:
            QMessageBox.critical(self, "Error", "No se obtuvieron detalles del producto.")
            return
        dialog = ProductFormDialog(product_data_to_edit=product_to_edit, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                success = ProductsController.update_existing_product(
                    product_id=self.current_selected_product_id, name=data['name'],
                    quantity_available=data['quantity_available'], sale_price=data['sale_price'],
                    purchase_price=data['purchase_price']
                )
                if success:
                    QMessageBox.information(self, "Éxito", f"Producto '{data['name']}' actualizado.")
                    self.load_products_and_setup_completer() # Recargar y actualizar completer
                else:
                    QMessageBox.warning(self, "Error", "No se pudo actualizar el producto.")

    def handle_delete_restore_product(self):
        if not self.current_selected_product_id:
            QMessageBox.warning(self, "Sin Selección", "Seleccione un producto.")
            return
        product_details = ProductsController.get_product_details(self.current_selected_product_id)
        if not product_details:
            QMessageBox.critical(self, "Error", "No se encontró el producto.")
            return
        is_currently_active = product_details['is_active']
        product_name = product_details['name']
        action_text_verb = "desactivar" if is_currently_active else "activar"
        action_text_past = "desactivado" if is_currently_active else "activado"
        confirm_message = f"¿Está seguro de {action_text_verb} el producto '{product_name}'?"
        reply = QMessageBox.question(self, f"Confirmar {action_text_verb.capitalize()}", confirm_message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success = False
            if is_currently_active:
                success = ProductsController.deactivate_product(self.current_selected_product_id)
            else:
                success = ProductsController.activate_product(self.current_selected_product_id)
            if success:
                QMessageBox.information(self, "Éxito", f"Producto '{product_name}' {action_text_past}.")
                self.load_products_and_setup_completer() # Recargar y actualizar completer
            else:
                QMessageBox.warning(self, "Error", f"No se pudo {action_text_verb} el producto.")