# utils/printer.py

import os
import datetime
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument # QImage no es necesaria si el logo se carga vía HTML
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QSizeF, QUrl # QUrl para el logo

class Printer:
    def __init__(self):
        pass

    def print_invoice(self, items, total_sale, paid_amount, change_amount, logo_path=None, 
                      store_name="Ferretería YD", # <--- CAMBIO DE NOMBRE
                      store_nit="9659228",        # <--- NUEVO DATO
                      store_phone="3229220286"):  # <--- NUEVO DATO
        printer = QPrinter(QPrinter.HighResolution)
        
        dialog = QPrintDialog(printer, None)
        if dialog.exec_() != QPrintDialog.Accepted:
            QMessageBox.information(None, "Impresión Cancelada", "La impresión de la factura ha sido cancelada por el usuario.")
            return False

        printer.setPageMargins(5.0, 10.0, 5.0, 10.0, QPrinter.Millimeter)

        doc = QTextDocument()

        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 9pt; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
                th, td {{ border-bottom: 1px dashed #ccc; padding: 3px; text-align: left; }}
                th {{ background-color: #f9f9f9; font-weight: bold; }}
                .header-info p, .store-details p {{ margin: 2px 0; }}
                .text-center {{ text-align: center; }}
                .text-right {{ text-align: right; }}
                .total-section td {{ font-weight: bold; border-top: 1px solid #000;}}
                .logo-container {{ text-align: center; margin-bottom: 5px; }} /* Reducido margen inferior */
                .logo-container img {{ max-width: 120px; max-height: 60px; }} /* Ajusta según tu logo */
            </style>
        </head>
        <body>
        """

        if logo_path and os.path.exists(logo_path):
            # Usar QUrl.fromLocalFile para asegurar que QTextDocument encuentre la imagen correctamente
            # y convertir barras invertidas a barras normales para URLs.
            logo_url = QUrl.fromLocalFile(os.path.abspath(logo_path)).toString()
            html_content += f"<div class='logo-container'><img src='{logo_url}' alt='Logo'></div>"
        
        html_content += f"<h2 class='text-center'>{store_name}</h2>"
        # Añadir NIT y Teléfono debajo del nombre de la tienda
        html_content += f"<div class='store-details text-center'>"
        html_content += f"<p>NIT: {store_nit}</p>"
        html_content += f"<p>Tel/WhatsApp: {store_phone}</p>"
        html_content += "</div>"
        html_content += "<p class='text-center'><strong>FACTURA DE VENTA</strong></p>"
        html_content += f"<div class='header-info text-center'>"
        html_content += f"<p>Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        html_content += "</div><hr>"

        html_content += "<table>"
        html_content += "<tr><th>Producto</th><th>Cant.</th><th>P. Unit.</th><th>Subtotal</th></tr>"

        for item_data in items:
            product_name, quantity, unit_price, subtotal = item_data # Desempaquetar
            html_content += f"<tr><td>{product_name}</td><td class='text-right'>{quantity}</td><td class='text-right'>{unit_price:.2f}</td><td class='text-right'>{subtotal:.2f}</td></tr>"
        
        html_content += "</table>"

        html_content += "<table class='total-section'>"
        html_content += f"<tr><td colspan='3'><strong>TOTAL:</strong></td><td class='text-right'><strong>{total_sale:.2f}</strong></td></tr>"
        html_content += f"<tr><td colspan='3'>Paga con:</td><td class='text-right'>{paid_amount:.2f}</td></tr>"
        html_content += f"<tr><td colspan='3'>Cambio:</td><td class='text-right'>{change_amount:.2f}</td></tr>"
        html_content += "</table>"
        html_content += "<hr>"
        html_content += "<p class='text-center'>¡Gracias por su compra!</p>"
        html_content += "</body></html>"

        doc.setHtml(html_content)
        
        # Para depuración, puedes guardar el HTML a un archivo:
        # with open("factura_debug.html", "w", encoding="utf-8") as f:
        #     f.write(html_content)
        # printer.setOutputFormat(QPrinter.PdfFormat)
        # printer.setOutputFileName("factura_test.pdf")

        doc.print_(printer)

        if printer.printerState() == QPrinter.Error:
            error_message = f"No se pudo imprimir la factura. Estado de la impresora: {printer.printerState()}."
            QMessageBox.critical(None, "Error de Impresión", error_message)
            print(error_message)
            return False
        
        return True