from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QDateEdit, QPushButton, QMessageBox, QSizePolicy)
from PyQt5.QtCore import QDate, Qt
from app.controllers.history_controller import HistoryController

class HistoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = HistoryController()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Filtros por fecha
        filter_layout = QHBoxLayout()
        
        start_label = QLabel("Desde:")
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        
        end_label = QLabel("Hasta:")
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        
        filter_btn = QPushButton("Filtrar")
        filter_btn.clicked.connect(self.filter_sales)
        
        filter_layout.addWidget(start_label)
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(end_label)
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(filter_btn)
        filter_layout.addStretch()

        # Tabla de ventas
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(4)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Fecha", "Base Inicial", "Total"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.doubleClicked.connect(self.show_sale_details)

        layout.addLayout(filter_layout)
        layout.addWidget(self.sales_table)

        self.setLayout(layout)
        self.filter_sales()  # Cargar datos iniciales

    def filter_sales(self):
        """Filtrar ventas por rango de fechas"""
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        sales = self.controller.get_sales_by_date_range(start, end)
        self.sales_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale[0])))
            self.sales_table.setItem(row, 1, QTableWidgetItem(sale[1]))
            self.sales_table.setItem(row, 2, QTableWidgetItem(f"${sale[2]:,.2f}"))
            self.sales_table.setItem(row, 3, QTableWidgetItem(f"${sale[3]:,.2f}"))

    def show_sale_details(self, index):
        """Mostrar detalles de la venta seleccionada"""
        sale_id = int(self.sales_table.item(index.row(), 0).text())
        details = self.controller.get_sale_details(sale_id)
        
        if details:
            msg = QMessageBox()
            msg.setWindowTitle(f"Detalles de Venta - {details['fecha']}")
            msg.setIcon(QMessageBox.Information)
            
            text = f"<b>Base del día:</b> ${details['base_inicial']:,.2f}<br><br>"
            text += "<table width='100%' border='1' cellpadding='4'>"
            text += "<tr><th>Producto</th><th>Cantidad</th><th>P. Unitario</th><th>Subtotal</th></tr>"
            
            for item in details['items']:
                text += f"<tr><td>{item[0]}</td><td align='right'>{item[1]}</td>"
                text += f"<td align='right'>${item[2]:,.2f}</td><td align='right'>${item[3]:,.2f}</td></tr>"
            
            text += "</table><br>"
            text += f"<b>Total General:</b> ${details['total']:,.2f}"
            
            msg.setText(text)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()