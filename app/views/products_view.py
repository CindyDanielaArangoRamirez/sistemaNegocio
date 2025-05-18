# app/views/products_view.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QFrame,
    QCompleter # <--- IMPORTACIÓN IMPORTANTE
)
from PyQt5.QtCore import Qt, QStringListModel, QEvent # QStringListModel para el QCompleter
from PyQt5.QtGui import QPalette, QColor, QIntValidator, QDoubleValidator, QValidator 
from app.controllers.products_controller import ProductsController
# ProductFormDialog debería estar aquí o importado si está en dialogs.py
# class ProductFormDialog(QDialog): ... (como lo teníamos antes)

# --- Diálogo Personalizado para Agregar/Editar Productos (Incluido aquí por completitud) ---
# Si lo tienes en dialogs.py, solo necesitas importarlo.
class ProductFormDialog(QDialog):
    def __init__(self, product_data_to_edit=None, parent=None):
        super().__init__(parent)
        self.product_data_to_edit = product_data_to_edit

        self.original_text_color = self.palette().color(QPalette.Text)

        if self.product_data_to_edit:
            self.setWindowTitle("Editar Producto")
        else:
            self.setWindowTitle("Agregar Nuevo Producto")
        
        self.setMinimumWidth(400)
        self.init_form_ui()

        if self.product_data_to_edit:
            self.populate_form_for_edit()
        else:
            # Establecer apariencia inicial de placeholders
            self.update_lineedit_appearance(self.quantity_lineedit, is_placeholder=True)
            self.update_lineedit_appearance(self.purchase_price_lineedit, is_placeholder=True)
            self.update_lineedit_appearance(self.sale_price_lineedit, is_placeholder=True)

    def init_form_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_lineedit = QLineEdit()
        self.name_lineedit.setPlaceholderText("Ej: Martillo de Uña")
        form_layout.addRow("Nombre del Producto:", self.name_lineedit)

        self.quantity_lineedit = QLineEdit()
        self.quantity_lineedit.setPlaceholderText("Cantidad") # Placeholder textual
        self.quantity_int_validator = QIntValidator(0, 99999, self) # Rango: 0 a 99999
        self.quantity_lineedit.setValidator(self.quantity_int_validator)
        form_layout.addRow("Cantidad Disponible:", self.quantity_lineedit)

        self.purchase_price_lineedit = QLineEdit()
        self.purchase_price_lineedit.setPlaceholderText("0.00") # Placeholder textual
        # QDoubleValidator(bottom, top, decimals, parent)
        # Nota: QLocale puede afectar cómo QDoubleValidator interpreta decimales (',' vs '.')
        self.purchase_price_validator = QDoubleValidator(0.00, 999999.99, 2, self)
        self.purchase_price_validator.setNotation(QDoubleValidator.StandardNotation) # Asegura que use '.'
        self.purchase_price_lineedit.setValidator(self.purchase_price_validator)
        # Podríamos añadir el "$ " como un QLabel al lado o confiar en la etiqueta del formulario.
        # Si quieres el "$ " dentro, es más complicado con QLineEdit y placeholder gris.
        # Por simplicidad, lo omitimos del campo de entrada por ahora.
        form_layout.addRow("Precio de Compra ($):", self.purchase_price_lineedit)


        self.sale_price_lineedit = QLineEdit()
        self.sale_price_lineedit.setPlaceholderText("0.00") # Placeholder textual
        self.sale_price_validator = QDoubleValidator(0.00, 999999.99, 2, self)
        self.sale_price_validator.setNotation(QDoubleValidator.StandardNotation)
        self.sale_price_lineedit.setValidator(self.sale_price_validator)
        form_layout.addRow("Precio de Venta ($):", self.sale_price_lineedit)

        for le in [self.quantity_lineedit, self.purchase_price_lineedit, self.sale_price_lineedit]:
            le.installEventFilter(self)
            le.textChanged.connect(lambda text, line_edit=le: self.update_lineedit_appearance(line_edit))

        
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


    def set_lineedit_text_color(self, line_edit_widget, color):
            if line_edit_widget:
                palette = line_edit_widget.palette()
                palette.setColor(QPalette.Text, color)
                line_edit_widget.setPalette(palette)

    def update_lineedit_appearance(self, line_edit, is_placeholder=None):
        """Actualiza la apariencia (color de texto) de un QLineEdit."""
        if is_placeholder is None: # Determinar si es placeholder por el texto vacío
            is_placeholder = (line_edit.text() == "")
            
        if is_placeholder and not line_edit.hasFocus():
            self.set_lineedit_text_color(line_edit, Qt.gray)
        else:
            self.set_lineedit_text_color(line_edit, self.original_text_color)


    def eventFilter(self, obj, event):
        target_line_edits = [
            self.quantity_lineedit,
            self.purchase_price_lineedit,
            self.sale_price_lineedit
        ]
        if obj in target_line_edits:
            if event.type() == QEvent.Type.FocusIn:
                obj.selectAll() # QLineEdit maneja bien selectAll()
                self.update_lineedit_appearance(obj, is_placeholder=False) # Color normal al enfocar
            elif event.type() == QEvent.Type.FocusOut:
                self.update_lineedit_appearance(obj) # Actualizar color al desenfocar
            
        return super().eventFilter(obj, event)


    def populate_form_for_edit(self):
        if self.product_data_to_edit:
            self.name_lineedit.setText(self.product_data_to_edit['name'])

            # Para campos numéricos, necesitamos un valor por defecto si la columna pudiera no existir
            # o si quieres manejar un None explícitamente, aunque con sqlite3.Row si la columna
            # no está en el SELECT, dará un IndexError o KeyError.
            # Es mejor asegurarse que el SELECT en get_product_details trae todas las columnas necesarias.

            quantity_val = ''
            if 'quantity_available' in self.product_data_to_edit.keys():
                quantity_val = self.product_data_to_edit['quantity_available']
            self.quantity_lineedit.setText(str(quantity_val))

            purchase_price_val = 0.0
            if 'purchase_price' in self.product_data_to_edit.keys():
                purchase_price_val = self.product_data_to_edit['purchase_price']
            # --- CAMBIO AQUÍ ---
            # Formatear explícitamente a un string con dos decimales usando punto
            self.purchase_price_lineedit.setText(f"{float(purchase_price_val):.2f}") 

            sale_price_val = 0.0
            if 'sale_price' in self.product_data_to_edit.keys():
                sale_price_val = self.product_data_to_edit['sale_price']
            # --- CAMBIO AQUÍ ---
            self.sale_price_lineedit.setText(f"{float(sale_price_val):.2f}")
            
            # Actualizar apariencia después de poblar
            self.update_lineedit_appearance(self.quantity_lineedit)
            self.update_lineedit_appearance(self.purchase_price_lineedit)
            self.update_lineedit_appearance(self.sale_price_lineedit)

    def get_data(self):
        name = self.name_lineedit.text().strip()
        if not name: 
            QMessageBox.warning(self, "Dato Faltante", "El nombre del producto no puede estar vacío.")
            return None

        # --- Obtener y validar cantidad ---
        quantity_str = self.quantity_lineedit.text().strip()
        quantity = 0
        if quantity_str:
            try:
                temp_quantity = int(quantity_str)
                # Validar rango para cantidad (QIntValidator también lo hace, pero por si acaso)
                if not (0 <= temp_quantity <= 99999): # Mismo rango que tu QIntValidator
                    QMessageBox.warning(self, "Entrada Inválida", 
                                        "La cantidad está fuera del rango permitido (0-99999).")
                    self.quantity_lineedit.setFocus()
                    return None
                quantity = temp_quantity
            except ValueError:
                QMessageBox.warning(self, "Entrada Inválida", 
                                    "La cantidad ingresada no es un número entero válido.")
                self.quantity_lineedit.setFocus()
                return None
        
        # Definir el rango de precios una vez
        min_price = 0.00
        max_price = 999999.99

        # --- Obtener y validar precio de compra ---
        purchase_price_str = self.purchase_price_lineedit.text().strip()
        purchase_price = 0.0
        if purchase_price_str:
            try:
                # Intentar convertir directamente, normalizando la coma
                temp_purchase_price = float(purchase_price_str.replace(',', '.'))
                
                # Validar el rango manualmente
                if not (min_price <= temp_purchase_price <= max_price):
                    QMessageBox.warning(self, "Entrada Inválida", 
                                        f"El precio de compra está fuera del rango permitido ({min_price:.2f} - {max_price:.2f}).")
                    self.purchase_price_lineedit.setFocus()
                    return None
                
                # Redondear a 2 decimales para consistencia (opcional, pero bueno para la BD)
                purchase_price = round(temp_purchase_price, 2)

            except ValueError:
                QMessageBox.warning(self, "Entrada Inválida", 
                                    "El precio de compra debe ser un número decimal válido (ej. 123.45).")
                self.purchase_price_lineedit.setFocus()
                return None
        
        # --- Obtener y validar precio de venta ---
        sale_price_str = self.sale_price_lineedit.text().strip()
        sale_price = 0.0
        if sale_price_str:
            try:
                temp_sale_price = float(sale_price_str.replace(',', '.'))

                if not (min_price <= temp_sale_price <= max_price):
                    QMessageBox.warning(self, "Entrada Inválida", 
                                        f"El precio de venta está fuera del rango permitido ({min_price:.2f} - {max_price:.2f}).")
                    self.sale_price_lineedit.setFocus()
                    return None
                
                sale_price = round(temp_sale_price, 2)

            except ValueError:
                QMessageBox.warning(self, "Entrada Inválida", 
                                    "El precio de venta debe ser un número decimal válido (ej. 123.45).")
                self.sale_price_lineedit.setFocus()
                return None
        
        print(f"DEBUG get_data - Datos validados: Cant: {quantity}, Compra: {purchase_price}, Venta: {sale_price}") # DEBUG FINAL
        
        return {'name': name, 'quantity_available': quantity,
                'purchase_price': purchase_price, 'sale_price': sale_price}

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