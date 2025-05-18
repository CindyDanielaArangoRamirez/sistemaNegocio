# app/views/sales_view.py
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QCompleter,
    QHeaderView, QFrame, QDialog
)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QDoubleValidator, QIntValidator

from app.controllers.sales_controller import SalesController
from app.controllers.products_controller import ProductsController
from .dialogs import InvoiceDialog 
from utils.helpers import resource_path # Sigue siendo útil si cargas otros recursos en esta vista
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
            # Es mejor manejar esto de forma más robusta, quizás no permitiendo que SalesView se cree
            # o mostrando un estado deshabilitado hasta que el usuario sea válido.
            QMessageBox.critical(self, "Error Usuario", "Usuario no identificado para ventas. La funcionalidad de ventas puede estar limitada.")
            # Considera si la aplicación debe continuar en este estado.

        self.current_sale_items_list = []
        self.base_amount_registered = 0.0 # Podrías inicializarlo a None y verificarlo
        self.product_cache_for_sale = {}
        self.all_product_names_for_completer = []
        self.printer_service = Printer()
        self.store_name = "Ferretería YD" # Nombre de tu tienda
        self.store_nit = "9659228"       # NIT de tu tienda
        self.store_phone = "3229220286"  # Teléfono de tu tienda

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
        
        self.sales_view_product_completer = QCompleter(self)
        self.sales_view_product_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.sales_view_product_completer.setFilterMode(Qt.MatchStartsWith)
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
        
        completer_model = QStringListModel(self.all_product_names_for_completer)
        self.sales_view_product_completer.setModel(completer_model)
        self.display_low_stock_warning()

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
        if not base_text: QMessageBox.warning(self, "Campo Vacío", "Ingrese base inicial."); return
        try:
            base_val = float(base_text)
            if base_val < 0: raise ValueError("Base negativa.")
        except ValueError as e:
            QMessageBox.warning(self, "Monto Inválido", f"Ingrese monto válido.\n{e}"); return
        
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
        if not product_name_typed or not quantity_text: QMessageBox.warning(self, "Campos Incompletos", "Ingrese producto y cantidad."); return
        try:
            quantity_to_add = int(quantity_text)
            if quantity_to_add <= 0: raise ValueError("Cantidad debe ser positiva.")
        except ValueError as e:
            QMessageBox.warning(self, "Cantidad Inválida", f"Ingrese una cantidad numérica válida.\n{e}"); return
        
        product_data_from_cache = self.product_cache_for_sale.get(product_name_typed.lower())
        if not product_data_from_cache: QMessageBox.warning(self, "Producto Desconocido", f"Producto '{product_name_typed}' no encontrado en caché."); return
        
        current_quantity_in_cart = sum(item['quantity_sold'] for item in self.current_sale_items_list if item['product_id'] == product_data_from_cache['id'])
        
        if (current_quantity_in_cart + quantity_to_add) > product_data_from_cache['quantity_available']:
            QMessageBox.warning(self, "Stock Insuficiente",
                f"Stock de '{product_data_from_cache['name']}': {product_data_from_cache['quantity_available']}. "
                f"Ya en carrito: {current_quantity_in_cart}. Solicitados ahora: {quantity_to_add}.")
            return

        item_found_in_list = False
        for item in self.current_sale_items_list:
            if item['product_id'] == product_data_from_cache['id']:
                item['quantity_sold'] += quantity_to_add
                item['subtotal'] = item['quantity_sold'] * item['price_per_unit']
                item_found_in_list = True; break
        if not item_found_in_list:
            self.current_sale_items_list.append({
                'product_id': product_data_from_cache['id'], 'name': product_data_from_cache['name'],
                'quantity_sold': quantity_to_add, 'price_per_unit': product_data_from_cache['sale_price'],
                'subtotal': quantity_to_add * product_data_from_cache['sale_price']
            })
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
            QMessageBox.warning(self, "Venta Vacía", "No hay productos para procesar.")
            return

        total_sale_amount = self.update_total_display() 

        invoice_dialog = InvoiceDialog(self.current_sale_items_list, total_sale_amount, self)
        
        if invoice_dialog.exec_() == QDialog.Accepted:
            dialog_results = invoice_dialog.get_dialog_results()
            customer_payment = dialog_results.get("customer_payment", 0.0)
            change_given = dialog_results.get("change_given", 0.0)
            should_print_invoice = dialog_results.get("print_invoice", False)

            items_for_controller = [{'product_id': i['product_id'], 'quantity_sold': i['quantity_sold'], 
                                     'price_per_unit': i['price_per_unit']} for i in self.current_sale_items_list]

            # Asegúrate de que SalesController.current_base_cash y self.user_id estén correctos
            # La llamada a process_new_sale en SalesController fue modificada para tomar solo 3 argumentos.
            # Si tu SalesController.process_new_sale espera self.base_amount_registered y self.user_id
            # necesitas pasarlos o asegurar que SalesController los obtenga de otra manera (ej. desde sus atributos de clase)
            sale_id = SalesController.process_new_sale(
                items_to_sell=items_for_controller, 
                total_sale_amount=total_sale_amount
                # base_amount=self.base_amount_registered, # Si tu controlador aún lo espera
                # user_id=self.user_id                    # Si tu controlador aún lo espera
            )
            # Si SalesController.process_new_sale usa SalesController.current_base_cash y 
            # SalesController.current_user_id, no necesitas pasarlos aquí.

            if sale_id:
                QMessageBox.information(self, "Venta Registrada", f"Venta ID {sale_id} ha sido procesada exitosamente.")

                if should_print_invoice:
                    items_to_print_tuples = [(item['name'], item['quantity_sold'], item['price_per_unit'], item['subtotal'])
                                             for item in self.current_sale_items_list]
                    
                    # --- LÓGICA DEL LOGO ELIMINADA DE LA LLAMADA A PRINT_INVOICE ---
                    try:
                        print_successful = self.printer_service.print_invoice(
                            items=items_to_print_tuples,
                            total_sale=total_sale_amount,
                            paid_amount=customer_payment,
                            change_amount=change_given,
                            # logo_path=None, # Ya no se pasa este argumento
                            store_name=self.store_name,
                            store_nit=self.store_nit,
                            store_phone=self.store_phone
                        )
                        if print_successful:
                            QMessageBox.information(self, "Impresión", "Factura enviada a la impresora.")
                    except TypeError as te: # Capturar específicamente el TypeError si la firma aún no coincide
                        QMessageBox.critical(self, "Error de Parámetro de Impresión", f"Error al llamar a la función de impresión: {te}\nAsegúrese de que printer.py no espere 'logo_path'.")
                        print(f"TypeError en print_invoice: {te}")
                    except Exception as e:
                        QMessageBox.critical(self, "Error de Impresión Inesperado", f"Ocurrió un error al intentar imprimir: {e}")
                
                self.reset_for_new_sale()
            else:
                QMessageBox.critical(self, "Error al Registrar Venta", "No se pudo registrar la venta en la base de datos.")
        else:
            QMessageBox.information(self, "Venta Cancelada", "El proceso de finalización de venta fue cancelado.")

    def handle_clear_current_sale(self):
        if self.current_sale_items_list:
            reply = QMessageBox.question(self, "Limpiar Venta", 
                                         "¿Está seguro de que desea limpiar todos los artículos de la venta actual?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.current_sale_items_list.clear()
                self.refresh_current_sale_table()
                self.product_name_search_lineedit.setFocus()
        else:
            QMessageBox.information(self, "Venta Vacía", "No hay artículos para limpiar.")

    def reset_for_new_sale(self):
        self.current_sale_items_list.clear()
        self.refresh_current_sale_table()
        self.product_name_search_lineedit.clear()
        self.item_quantity_lineedit.setText("1")
        self.display_low_stock_warning() 
        self.product_name_search_lineedit.setFocus()