from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QPainter, QTextDocument
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

class Printer:
    def print_invoice(self, items, total, payment, change, parent=None):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            printer.setOrientation(QPrinter.Portrait)
            
            # Configurar márgenes (corregido)
            printer.setPageMargins(10, 10, 10, 10, QPrinter.Millimeter)
            
            print_dialog = QPrintDialog(printer, parent)
            if print_dialog.exec_() != QPrintDialog.Accepted:
                return False
            
            html = self._generate_invoice_html(items, total, payment, change)
            
            doc = QTextDocument()
            doc.setHtml(html)
            
            painter = QPainter()
            if not painter.begin(printer):
                QMessageBox.warning(parent, "Error", "No se pudo iniciar la impresión")
                return False
            
            doc.drawContents(painter)
            painter.end()
            return True
            
        except Exception as e:
            QMessageBox.critical(
                parent, 
                "Error de Impresión", 
                f"No se pudo imprimir el recibo:\n{str(e)}"
            )
            return False
    
    def _generate_invoice_html(self, items, total, payment, change):
        """Generar HTML para la factura"""
        items_html = ""
        for item in items:
            items_html += f"""
            <tr>
                <td>{item['name']}</td>
                <td align="right">{item['quantity']}</td>
                <td align="right">${item['price']:,.2f}</td>
                <td align="right">${item['subtotal']:,.2f}</td>
            </tr>
            """
        
        return f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 12px; }}
            .header {{ text-align: center; margin-bottom: 15px; }}
            .title {{ font-size: 18px; font-weight: bold; }}
            .subtitle {{ font-size: 14px; color: #555; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th {{ background-color: #f2f2f2; text-align: left; padding: 5px; }}
            td {{ padding: 5px; border-bottom: 1px solid #ddd; }}
            .totals {{ margin-top: 20px; font-weight: bold; }}
            .footer {{ margin-top: 30px; text-align: center; font-style: italic; color: #777; }}
            .right {{ text-align: right; }}
        </style>
        </head>
        <body>
        <div class="header">
            <div class="title">Ferretería XYZ</div>
            <div class="subtitle">Factura de Venta</div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Producto</th>
                    <th class="right">Cant.</th>
                    <th class="right">P. Unit.</th>
                    <th class="right">Subtotal</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>
        
        <div class="totals">
            <div>Total: <span class="right">${total:,.2f}</span></div>
            <div>Pago: <span class="right">${payment:,.2f}</span></div>
            <div>Cambio: <span class="right">${change:,.2f}</span></div>
        </div>
        
        <div class="footer">
            Gracias por su compra!<br>
            Vuelva pronto
        </div>
        </body>
        </html>
        """