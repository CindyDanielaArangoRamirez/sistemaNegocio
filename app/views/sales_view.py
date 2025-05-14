# app/views/sales_view.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QCompleter, # <--- IMPORTACIÓN
    QHeaderView, QFrame, QDialog
)
from PyQt5.QtCore import Qt, QStringListModel # <--- QStringListModel
from PyQt5.QtGui import QDoubleValidator, QIntValidator

from app.controllers.sales_controller import SalesController
from app.controllers.products_controller import ProductsController
from .dialogs import InvoiceDialog # Asumiendo que InvoiceDialog está en el mismo directorio
from utils.printer import Printer

class SalesView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.current_user_data = user_data
        self.user_id = None
        if self.current_user_data:
            try: self.user_id = self.current_user_data['id']
            except (KeyError, TypeError, IndexError): print("Advertencia (SalesView): No se pudo obtener 'id' de user_data.")
        if self.user_id is None:
            QMessageBox.critical(self, "Error Usuario", "Usuario no identificado para ventas.")

        self.current_sale_items_list = []
        self.base_amount_registered = 0.0
        self.product_cache_for_sale = {}
        self.all_product_names_for_completer = [] # Esta lista se usará para el modelo del QCompleter
        self.printer_service = Printer()
        self.init_ui_layout()
        self.load_products_for_autocompleter_and_cache()
        self.update_total_display()

    def init_ui_layout(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20); main_layout.setSpacing(15)
        title_label = QLabel("Realizar Venta"); title_label.setObjectName("viewTitle")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        self.base_input_section_layout = QHBoxLayout(); self.base_input_section_layout.setSpacing(10)
        base_label = QLabel("Base Inicial del Día ($):"); base_label.setStyleSheet("font-weight: bold;")
        self.base_amount_lineedit = QLineEdit(); self.base_amount_lineedit.setPlaceholderText("Monto en caja")
        self.base_amount_lineedit.setValidator(QDoubleValidator(0, 99999999.99, 2))
        self.base_amount_lineedit.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        self.register_base_button = QPushButton("Registrar Base"); self.register_base_button.setObjectName("primaryButton")
        self.register_base_button.setStyleSheet("padding: 8px 12px;")
        self.register_base_button.clicked.connect(self.handle_base_registration)
        for widget in [base_label, self.base_amount_lineedit, self.register_base_button]: self.base_input_section_layout.addWidget(widget)
        self.base_input_section_layout.addStretch(); main_layout.addLayout(self.base_input_section_layout)

        self.sale_processing_section_widget = QWidget()
        sale_processing_main_layout = QVBoxLayout(self.sale_processing_section_widget)
        sale_processing_main_layout.setSpacing(15); sale_processing_main_layout.setContentsMargins(0,10,0,0)
        self.registered_base_info_label = QLabel("Base no registrada.")
        self.registered_base_info_label.setStyleSheet("font-style: italic; color: #7f8c8d;")
        sale_processing_main_layout.addWidget(self.registered_base_info_label)

        self.low_stock_warning_frame_sales = QFrame(); self.low_stock_warning_frame_sales.setObjectName("lowStockWarning")
        low_stock_layout = QHBoxLayout(self.low_stock_warning_frame_sales)
        self.low_stock_label_sales = QLabel(""); low_stock_layout.addWidget(self.low_stock_label_sales, 1)
        close_warning_btn = QPushButton("✕"); close_warning_btn.setObjectName("closeWarningButton")
        close_warning_btn.setFixedSize(20,20); close_warning_btn.clicked.connect(self.low_stock_warning_frame_sales.hide)
        low_stock_layout.addWidget(close_warning_btn); self.low_stock_warning_frame_sales.hide()
        self.low_stock_warning_frame_sales.setStyleSheet("""
            QFrame#lowStockWarning { background-color: #fcf8e3; border: 1px solid #faebcc; border-radius: 4px; padding: 8px; }
            QFrame#lowStockWarning QLabel { color: #8a6d3b; background-color: transparent; border: none; }
            QPushButton#closeWarningButton { background-color: transparent; border: none; color: #8a6d3b; font-weight: bold; }""")
        sale_processing_main_layout.addWidget(self.low_stock_warning_frame_sales)

        product_search_controls_layout = QHBoxLayout(); product_search_controls_layout.setSpacing(10)
        product_search_controls_layout.addWidget(QLabel("Producto:"))
        self.product_name_search_lineedit = QLineEdit()
        self.product_name_search_lineedit.setPlaceholderText("Escriba para buscar producto...")
        self.product_name_search_lineedit.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        # Configuración del QCompleter para SalesView
        self.sales_view_product_completer = QCompleter(self) # Renombrado para evitar confusión
        self.sales_view_product_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.sales_view_product_completer.setFilterMode(Qt.MatchStartsWith) # <--- IMPORTANTE PARA BÚSQUEDA POR INICIAL
        self.product_name_search_lineedit.setCompleter(self.sales_view_product_completer)
        
        product_search_controls_layout.addWidget(self.product_name_search_lineedit, 2)
        product_search_controls_layout.addWidget(QLabel("Cantidad:"))
        self.item_quantity_lineedit = QLineEdit("1")
        self.item_quantity_lineedit.setValidator(QIntValidator(1, 9999))
        self.item_quantity_lineedit.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        self.item_quantity_lineedit.setFixedWidth(80)
        product_search_controls_layout.addWidget(self.item_quantity_lineedit)
        self.add_item_button = QPushButton("➕ Agregar"); self.add_item_button.setObjectName("confirmButton")
        self.add_item_button.setStyleSheet("padding: 8px 12px;")
        self.add_item_button.clicked.connect(self.handle_add_item_to_current_sale)
        product_search_controls_layout.addWidget(self.add_item_button)
        sale_processing_main_layout.addLayout(product_search_controls_layout)
        
        self.current_sale_tablewidget = QTableWidget(); self.current_sale_tablewidget.setColumnCount(5)
        self.current_sale_tablewidget.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal", "Quitar"])
        header = self.current_sale_tablewidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5): header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.current_sale_tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.current_sale_tablewidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.current_sale_tablewidget.setMinimumHeight(150)
        sale_processing_main_layout.addWidget(self.current_sale_tablewidget)
        
        total_display_layout = QHBoxLayout()
        self.sale_total_display_label = QLabel("Total Venta: $0.00"); self.sale_total_display_label.setObjectName("totalAmountLabel")
        self.sale_total_display_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2c3e50; padding-top:10px;")
        total_display_layout.addStretch(); total_display_layout.addWidget(self.sale_total_display_label)
        sale_processing_main_layout.addLayout(total_display_layout)
        
        final_action_buttons_layout = QHBoxLayout(); final_action_buttons_layout.setSpacing(15)
        self.clear_current_sale_button = QPushButton("🗑️ Limpiar Venta"); self.clear_current_sale_button.setObjectName("warningButton")
        self.clear_current_sale_button.setStyleSheet("padding: 9px 15px;")
        self.clear_current_sale_button.clicked.connect(self.handle_clear_current_sale)
        self.finalize_sale_button = QPushButton("💰 Generar Venta"); self.finalize_sale_button.setObjectName("ctaButton")
        self.finalize_sale_button.setStyleSheet("padding: 9px 15px; font-weight:bold;")
        self.finalize_sale_button.clicked.connect(self.handle_finalize_sale_process)
        self.finalize_sale_button.setEnabled(False)
        final_action_buttons_layout.addStretch()
        final_action_buttons_layout.addWidget(self.clear_current_sale_button)
        final_action_buttons_layout.addWidget(self.finalize_sale_button)
        sale_processing_main_layout.addLayout(final_action_buttons_layout)
        
        self.sale_processing_section_widget.setEnabled(False)
        main_layout.addWidget(self.sale_processing_section_widget)
        self.setLayout(main_layout)

    def load_products_for_autocompleter_and_cache(self):
        self.product_cache_for_sale.clear()
        self.all_product_names_for_completer = []
        all_active_products = ProductsController.get_active_products_for_sales_view()
        if all_active_products:
            for prod_row in all_active_products:
                self.product_cache_for_sale[prod_row['name'].lower()] = dict(prod_row)
                self.all_product_names_for_completer.append(prod_row['name'])
        
        # Actualizar el modelo del QCompleter de SalesView
        completer_model = QStringListModel(self.all_product_names_for_completer)
        self.sales_view_product_completer.setModel(completer_model) # Usar el completer de SalesView
        
        self.display_low_stock_warning()

    # ... (resto de los métodos de SalesView: display_low_stock_warning, handle_base_registration,
    #      handle_add_item_to_current_sale, update_total_display, refresh_current_sale_table,
    #      handle_remove_item, handle_finalize_sale_process, handle_clear_current_sale, reset_for_new_sale
    #      permanecen igual que en la respuesta anterior) ...

    # Copio los métodos restantes para completitud, asumiendo que no hay más cambios en ellos por ahora:
    def display_low_stock_warning(self, threshold=5):
        low_stock_items = ProductsController.get_low_stock_products_for_alert(threshold)
        if low_stock_items:
            names = [item['name'] for item in low_stock_items]
            message = f"Stock bajo: {', '.join(names)}"
            if len(message) > 120: message = message[:117] + "..."
            self.low_stock_label_sales.setText(f"⚠️ {message}")
            self.low_stock_warning_frame_sales.show()
        else:
            self.low_stock_warning_frame_sales.hide()

    def handle_base_registration(self):
        if self.user_id is None:
            QMessageBox.critical(self, "Error Usuario", "Usuario no identificado.")
            return
        base_text = self.base_amount_lineedit.text().strip().replace(",",".")
        if not base_text:
            QMessageBox.warning(self, "Campo Vacío", "Ingrese base inicial.")
            return
        try:
            base_val = float(base_text)
            if base_val < 0: raise ValueError("Base negativa.")
        except ValueError as e:
            QMessageBox.warning(self, "Monto Inválido", f"Ingrese monto válido.\n{e}")
            return
        if SalesController.set_daily_base(base_val, self.user_id):
            self.base_amount_registered = base_val
            self.registered_base_info_label.setText(f"Base: ${self.base_amount_registered:,.2f}")
            self.registered_base_info_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            self.base_amount_lineedit.setEnabled(False); self.register_base_button.setEnabled(False)
            self.sale_processing_section_widget.setEnabled(True)
            self.product_name_search_lineedit.setFocus()
            self.display_low_stock_warning()
            QMessageBox.information(self, "Base Registrada", "Base registrada.")
        else:
            QMessageBox.critical(self, "Error", "No se pudo registrar la base.")

    def handle_add_item_to_current_sale(self):
        product_name_typed = self.product_name_search_lineedit.text().strip()
        quantity_text = self.item_quantity_lineedit.text().strip()
        if not product_name_typed or not quantity_text:
            QMessageBox.warning(self, "Campos Incompletos", "Ingrese producto y cantidad.")
            return
        try:
            quantity_to_add = int(quantity_text)
            if quantity_to_add <= 0: raise ValueError("Cantidad positiva.")
        except ValueError as e:
            QMessageBox.warning(self, "Cantidad Inválida", f"Cantidad numérica válida.\n{e}")
            return
        product_data_from_cache = self.product_cache_for_sale.get(product_name_typed.lower())
        if not product_data_from_cache:
            QMessageBox.warning(self, "Producto Desconocido", f"'{product_name_typed}' no encontrado.")
            return
        if quantity_to_add > product_data_from_cache['quantity_available']:
            QMessageBox.warning(self, "Stock Insuficiente",
                f"Stock de '{product_data_from_cache['name']}': {product_data_from_cache['quantity_available']}. Solicitados: {quantity_to_add}")
            return
        item_found = False
        for item in self.current_sale_items_list:
            if item['product_id'] == product_data_from_cache['id']:
                new_qty = item['quantity_sold'] + quantity_to_add
                if new_qty > product_data_from_cache['quantity_available']:
                    QMessageBox.warning(self, "Stock Insuficiente", f"No puede agregar más '{product_data_from_cache['name']}'. Límite.")
                    return
                item['quantity_sold'] = new_qty
                item['subtotal'] = new_qty * item['price_per_unit']
                item_found = True; break
        if not item_found:
            self.current_sale_items_list.append({
                'product_id': product_data_from_cache['id'], 'name': product_data_from_cache['name'],
                'quantity_sold': quantity_to_add, 'price_per_unit': product_data_from_cache['sale_price'],
                'subtotal': quantity_to_add * product_data_from_cache['sale_price']})
        self.refresh_current_sale_table()
        self.product_name_search_lineedit.clear(); self.item_quantity_lineedit.setText("1")
        self.product_name_search_lineedit.setFocus()

    def update_total_display(self):
        current_total = sum(item['subtotal'] for item in self.current_sale_items_list)
        self.sale_total_display_label.setText(f"Total Venta: ${current_total:,.2f}")
        self.finalize_sale_button.setEnabled(len(self.current_sale_items_list) > 0)
        return current_total

    def refresh_current_sale_table(self):
        self.current_sale_tablewidget.setRowCount(0)
        for row_idx, item_data in enumerate(self.current_sale_items_list):
            self.current_sale_tablewidget.insertRow(row_idx)
            self.current_sale_tablewidget.setItem(row_idx, 0, QTableWidgetItem(item_data['name']))
            self.current_sale_tablewidget.setItem(row_idx, 1, QTableWidgetItem(str(item_data['quantity_sold'])))
            self.current_sale_tablewidget.setItem(row_idx, 2, QTableWidgetItem(f"${item_data['price_per_unit']:,.2f}"))
            self.current_sale_tablewidget.setItem(row_idx, 3, QTableWidgetItem(f"${item_data['subtotal']:,.2f}"))
            remove_btn = QPushButton("➖"); remove_btn.setToolTip("Quitar item"); remove_btn.setObjectName("dangerButtonSmall")
            remove_btn.clicked.connect(lambda checked, r=row_idx: self.handle_remove_item(r))
            self.current_sale_tablewidget.setCellWidget(row_idx, 4, remove_btn)
        self.update_total_display()

    def handle_remove_item(self, row_index_to_remove):
        if 0 <= row_index_to_remove < len(self.current_sale_items_list):
            del self.current_sale_items_list[row_index_to_remove]
            self.refresh_current_sale_table()

    def handle_finalize_sale_process(self):
        if not self.current_sale_items_list:
            QMessageBox.warning(self, "Venta Vacía", "No hay productos.")
            return
        total_sale_amount = self.update_total_display()
        invoice_dialog = InvoiceDialog(self.current_sale_items_list, total_sale_amount, self)
        if invoice_dialog.exec_() == QDialog.Accepted:
            dialog_results = invoice_dialog.get_dialog_results()
            items_for_controller = [{'product_id': i['product_id'], 'quantity_sold': i['quantity_sold'], 'price_per_unit': i['price_per_unit']}
                                    for i in self.current_sale_items_list]
            sale_id = SalesController.process_new_sale(items_for_controller, total_sale_amount)
            if sale_id:
                QMessageBox.information(self, "Venta Registrada", f"Venta ID {sale_id} procesada.")
                if dialog_results["print_invoice"]:
                    try:
                        items_to_print = [{'name':i['name'], 'quantity':i['quantity_sold'], 'unit_price':i['price_per_unit'], 'total_price':i['subtotal']}
                                          for i in self.current_sale_items_list]
                        self.printer_service.print_invoice(items_to_print, total_sale_amount, dialog_results["customer_payment"], dialog_results["change_given"])
                        QMessageBox.information(self, "Impresión", "Factura enviada (simulado).")
                    except AttributeError as ae:
                         QMessageBox.critical(self, "Error Impresión", f"Error impresora: {ae}")
                    except Exception as e:
                        QMessageBox.critical(self, "Error Impresión", f"No se pudo imprimir: {e}")
                self.reset_for_new_sale()
            else:
                QMessageBox.critical(self, "Error Venta", "No se pudo registrar la venta.")
        else:
            QMessageBox.information(self, "Venta Cancelada", "Finalización cancelada.")

    def handle_clear_current_sale(self):
        if self.current_sale_items_list:
            if QMessageBox.question(self, "Limpiar Venta", "¿Limpiar items?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
                self.current_sale_items_list = []; self.refresh_current_sale_table()
        else:
            QMessageBox.information(self, "Venta Vacía", "No hay items.")

    def reset_for_new_sale(self):
        self.current_sale_items_list = []; self.refresh_current_sale_table()
        self.product_name_search_lineedit.clear(); self.item_quantity_lineedit.setText("1")
        self.load_products_for_autocompleter_and_cache()
        self.product_name_search_lineedit.setFocus()