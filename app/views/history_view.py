# app/views/history_view.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTreeWidget, QTreeWidgetItem, QHeaderView,
    QDateEdit, QPushButton, QMessageBox, QFrame # QFrame para agrupar filtros
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont # Para poner texto en negrita
# Importar el controlador actualizado
from app.controllers.history_controller import HistoryController # Usa los métodos estáticos

class HistoryView(QWidget):
    def __init__(self):
        super().__init__()
        # No es necesario instanciar el controlador si usas métodos estáticos
        # self.controller = HistoryController()
        self.all_history_data_cache = {} # Cache para todos los datos del historial
        self.init_ui()
        self.load_and_display_history() # Carga inicial de todo el historial

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Historial de Ventas")
        title_label.setObjectName("viewTitle") # Para CSS
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # --- Sección de Filtros ---
        filter_section_frame = QFrame()
        filter_section_frame.setObjectName("sectionFrame") # Para estilo CSS
        filter_controls_layout = QVBoxLayout(filter_section_frame)

        date_filter_layout = QHBoxLayout()
        date_filter_layout.addWidget(QLabel("Filtrar por fecha específica:"))
        self.date_filter_edit = QDateEdit()
        self.date_filter_edit.setCalendarPopup(True)
        self.date_filter_edit.setDate(QDate.currentDate())
        self.date_filter_edit.setDisplayFormat("dd/MM/yyyy")
        date_filter_layout.addWidget(self.date_filter_edit)

        self.apply_date_filter_button = QPushButton("🔍 Aplicar Filtro")
        self.apply_date_filter_button.clicked.connect(self.handle_apply_date_filter)
        date_filter_layout.addWidget(self.apply_date_filter_button)

        self.show_all_history_button = QPushButton("🔄 Mostrar Todo")
        self.show_all_history_button.clicked.connect(self.load_and_display_history) # Recarga todo
        date_filter_layout.addWidget(self.show_all_history_button)
        date_filter_layout.addStretch()
        filter_controls_layout.addLayout(date_filter_layout)
        # Aquí podrías añadir más filtros si es necesario (ej. por rango de fechas, etc.)
        main_layout.addWidget(filter_section_frame)
        # --- Fin Sección de Filtros ---

        # --- Árbol para mostrar el Historial ---
        self.history_tree_widget = QTreeWidget()
        self.history_tree_widget.setObjectName("historyTree") # Para CSS
        self.history_tree_widget.setHeaderLabels(["Fecha / Detalle de Venta", "Cantidad", "Precio Unit.", "Subtotal"])
        header = self.history_tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.resizeSection(0, 550) # Dale un ancho inicial generoso
        header.resizeSection(1, 200)
        header.resizeSection(2, 200)
        header.resizeSection(3, 200)
        header.setStretchLastSection(False) # Importante

        self.history_tree_widget.setAlternatingRowColors(True)
        self.history_tree_widget.setEditTriggers(QTreeWidget.NoEditTriggers) # No editable
        # self.history_tree_widget.doubleClicked.connect(self.show_details_for_selected_item) # Si quieres detalles al doble clic
        main_layout.addWidget(self.history_tree_widget)
        # --- Fin Árbol de Historial ---

        # --- Botón para Borrar Historial ---
        bottom_controls_layout = QHBoxLayout()
        bottom_controls_layout.addStretch() # Empujar a la derecha
        self.delete_all_history_button = QPushButton("🗑️ Borrar Todo el Historial")
        self.delete_all_history_button.setObjectName("dangerButton") # Para estilo CSS (rojo)
        self.delete_all_history_button.clicked.connect(self.handle_confirm_delete_all_history)
        bottom_controls_layout.addWidget(self.delete_all_history_button)
        main_layout.addLayout(bottom_controls_layout)
        # --- Fin Botón Borrar ---

        self.setLayout(main_layout)

    def load_and_display_history(self, date_to_filter_ymd=None): # date_to_filter_ymd en formato 'YYYY-MM-DD'
        """Carga todos los datos del historial y los muestra, opcionalmente filtrados por una fecha."""
        if not self.all_history_data_cache or date_to_filter_ymd is None: # Cargar del controlador solo si no hay cache o se pide todo
            self.all_history_data_cache = HistoryController.get_formatted_sales_history()

        self.history_tree_widget.clear() # Limpiar el árbol

        if not self.all_history_data_cache:
            # Opcional: Mostrar un mensaje en el árbol si no hay historial
            no_data_item = QTreeWidgetItem(self.history_tree_widget, ["No hay historial de ventas disponible."])
            return

        # Ordenar las fechas (claves del diccionario) de forma descendente
        try:
            sorted_dates_ymd = sorted(
                self.all_history_data_cache.keys(),
                key=lambda d: QDate.fromString(d, "yyyy-MM-dd"),
                reverse=True
            )
        except Exception: # Fallback si las fechas no son parseables (no debería ocurrir)
            sorted_dates_ymd = sorted(self.all_history_data_cache.keys(), reverse=True)


        bold_font = QFont()
        bold_font.setBold(True)

        for sale_date_ymd_str in sorted_dates_ymd:
            if date_to_filter_ymd and sale_date_ymd_str != date_to_filter_ymd:
                continue # Omitir si no es la fecha filtrada

            daily_sale_data = self.all_history_data_cache[sale_date_ymd_str]
            
            # Formatear fecha a DD/MM/YYYY para mostrar
            q_date_obj = QDate.fromString(sale_date_ymd_str, "yyyy-MM-dd")
            display_date_str = q_date_obj.toString("dd/MM/yyyy") if q_date_obj.isValid() else sale_date_ymd_str

            # Crear el item principal para la fecha
            date_tree_item = QTreeWidgetItem(self.history_tree_widget, [display_date_str])
            date_tree_item.setFont(0, bold_font) # Fecha en negrita
            date_tree_item.setFlags(date_tree_item.flags() & ~Qt.ItemIsSelectable) # No seleccionable como tal

            # Añadir los items de producto vendidos ese día
            if daily_sale_data.get('items'):
                for item_detail in daily_sale_data['items']:
                    # Formato: ["  Producto", "Cantidad", "Precio Unit.", "Subtotal"]
                    product_sub_item = QTreeWidgetItem(date_tree_item)
                    product_sub_item.setText(0, f"    🛍️ {item_detail.get('product_name', 'N/A')}") # Nombre indentado
                    product_sub_item.setText(1, str(item_detail.get('quantity', 0)))
                    product_sub_item.setText(2, f"${item_detail.get('unit_sale_price_at_transaction', 0.0):.2f}")
                    product_sub_item.setText(3, f"${item_detail.get('total_sale_price', 0.0):.2f}")
            else:
                no_items_today = QTreeWidgetItem(date_tree_item, ["    (No se vendieron items individuales este día)"])
                no_items_today.setDisabled(True)


            # Añadir la información de resumen del día (Base, Total Ventas, Ganancias)
            summary_font = QFont() # Podría ser diferente si quieres
            # summary_font.setItalic(True)

            base_amount_str = f"    💵 Base del Día: ${daily_sale_data.get('base_amount', 0.0):.2f}"
            base_info_item = QTreeWidgetItem(date_tree_item, [base_amount_str])
            base_info_item.setFont(0, summary_font)
            base_info_item.setDisabled(True) # No interactuable

            total_sales_str = f"    💰 Total Ventas del Día: ${daily_sale_data.get('total_day_sales_value', 0.0):.2f}"
            total_sales_item = QTreeWidgetItem(date_tree_item, [total_sales_str])
            total_sales_item.setFont(0, summary_font)
            total_sales_item.setDisabled(True)

            profit_str = f"    📈 Ganancias del Día: ${daily_sale_data.get('net_profit', 0.0):.2f}"
            profit_item = QTreeWidgetItem(date_tree_item, [profit_str])
            profit_item.setFont(0, summary_font)
            profit_item.setDisabled(True)
            
            self.history_tree_widget.expandItem(date_tree_item) # Expandir por defecto para ver detalles

    def handle_apply_date_filter(self):
        """Aplica el filtro por la fecha seleccionada en QDateEdit."""
        selected_qdate = self.date_filter_edit.date()
        date_to_filter_ymd_str = selected_qdate.toString("yyyy-MM-dd") # Formato YYYY-MM-DD
        self.load_and_display_history(date_to_filter_ymd=date_to_filter_ymd_str)

    def handle_confirm_delete_all_history(self):
        """Pide confirmación y luego borra todo el historial de ventas."""
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación Total",
            "<b>¡ADVERTENCIA!</b> Esta acción eliminará permanentemente TODO el historial de ventas.\n"
            "Esta operación no se puede deshacer.\n\n"
            "¿Está absolutamente seguro de que desea continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Botón por defecto
        )

        if reply == QMessageBox.Yes:
            success = HistoryController.clear_all_sales_history()
            if success:
                QMessageBox.information(self, "Historial Eliminado", "Todo el historial de ventas ha sido eliminado.")
                self.all_history_data_cache.clear() # Limpiar cache
                self.load_and_display_history() # Recargar la vista (mostrará que está vacía)
            else:
                QMessageBox.critical(self, "Error de Eliminación", "No se pudo eliminar el historial de ventas.")

    # La función show_sale_details que tenías antes no aplica directamente al QTreeWidget
    # de la misma manera. Si quieres ver detalles de una venta específica (un grupo de items bajo una fecha),
    # podrías implementar algo al hacer doble clic en un item de producto dentro del árbol,
    # pero la información principal ya está visible.
    # def show_details_for_selected_item(self, item, column):
    #     # 'item' es un QTreeWidgetItem. Determinar si es un item de producto.
    #     # y luego mostrar más detalles si es necesario.
    #     parent = item.parent()
    #     if parent and parent != self.history_tree_widget.invisibleRootItem(): # Es un sub-item (producto o resumen)
    #         if "Base del Día" not in item.text(0) and \
    #            "Total Ventas" not in item.text(0) and \
    #            "Ganancias" not in item.text(0) and \
    #            "(No se vendieron items)" not in item.text(0):
    #             # Es un item de producto
    #             product_name = item.text(0).strip().replace("🛍️ ", "")
    #             # Aquí podrías buscar más datos del 'sale_id' o 'product_id' si los hubieras almacenado en el item
    #             # con item.setData(0, Qt.UserRole, sale_id) por ejemplo.
    #             QMessageBox.information(self, "Detalle Item", f"Detalles para: {product_name}\n(Implementación pendiente)")
    #         else:
    #             # Es un item de resumen, no hacer nada al doble clic
    #             pass