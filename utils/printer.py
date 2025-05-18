# utils/printer.py

import os
import datetime
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument, QPageSize, QPageLayout
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QSizeF, QMarginsF # QUrl ya no es necesaria

class Printer:
    def __init__(self):
        pass

    def print_invoice(self, items, total_sale, paid_amount, change_amount,
                      # logo_path ya no se pasa como argumento
                      store_name="Ferretería YD",
                      store_nit="9659228",
                      store_phone="3229220286"):
        
        printer = QPrinter(QPrinter.HighResolution)
        
        page_layout = QPageLayout()
        # Ancho de papel típico para Epson TM-T20III es 80mm o 58mm. Usaremos 80mm como base.
        # Si tu papel es de 58mm, cambia 80 a 58 y el width en CSS a ~50mm o 52mm.
        roll_paper_size = QPageSize(QSizeF(80, 3276), QPageSize.Unit.Millimeter, "RollPaper80mm")
        page_layout.setPageSize(roll_paper_size)
        page_layout.setMargins(QMarginsF(2.0, 3.0, 2.0, 3.0))
        page_layout.setOrientation(QPageLayout.Orientation.Portrait)
        
        printer.setPageLayout(page_layout)

        dialog = QPrintDialog(printer, None)
        if dialog.exec_() != QPrintDialog.Accepted:
            QMessageBox.information(None, "Impresión Cancelada", "La impresión de la factura ha sido cancelada por el usuario.")
            return False

        doc = QTextDocument()

        # Ajustes en CSS para mejor encaje en recibo
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ 
                    font-family: 'Courier New', Courier, monospace; /* Fuente monoespaciada común para recibos */
                    font-size: 7.5pt; /* Tamaño pequeño para más contenido */
                    width: 72mm; /* (80mm papel - 2mm margen izq - 2mm margen der = 76mm. 72mm para seguridad) */
                    margin: 0; 
                    padding: 0;
                    line-height: 1.2; /* Espaciado de línea ajustado */
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-bottom: 3px; /* Reducido */
                }}
                th, td {{ 
                    /* border-bottom: 1px dashed #ccc;  QUITAR BORDES INTERNOS DE TABLA PARA AHORRAR ESPACIO */
                    padding: 1px; /* Padding mínimo */
                    text-align: left; 
                    vertical-align: top; /* Para que el texto largo se alinee bien */
                    word-wrap: break-word;
                    word-break: break-all; /* Forzar quiebre si una palabra es muy larga */
                }}
                th {{ 
                    /* background-color: #f9f9f9; */ /* Quitar fondo para ahorrar tinta/espacio */
                    font-weight: bold; 
                    border-bottom: 1px solid #000; /* Línea solo debajo de encabezados */
                }}
                .store-info-header {{
                    text-align: center;
                    margin-bottom: 3px;
                }}
                .store-info-header h2 {{ 
                    font-size: 10pt; 
                    margin: 0 0 1px 0; 
                    font-weight: bold;
                }}
                .store-info-header p {{ 
                    font-size: 7pt; 
                    margin: 0; 
                }}
                .invoice-title p {{
                    text-align: center;
                    font-size: 8.5pt;
                    margin-top: 2px;
                    margin-bottom: 2px;
                    font-weight: bold;
                }}
                .date-time p {{
                    text-align: center;
                    font-size: 7pt;
                    margin-bottom: 2px;
                }}
                .text-right {{ text-align: right; }}
                .total-section td {{ 
                    font-weight: bold; 
                    padding-top: 2px; /* Pequeño espacio antes del total */
                    border-top: 1px solid #000; /* Línea encima del total */
                }}
                hr {{ 
                    border: none; 
                    border-top: 1px dashed #555; /* Línea punteada más sutil */
                    margin-top: 2px; 
                    margin-bottom: 2px; 
                }}
                .footer-message p {{
                    text-align: center;
                    font-size: 7pt;
                    margin-top: 3px;
                }}
            </style>
        </head>
        <body>
        """
        # --- SECCIÓN DEL LOGO ELIMINADA ---

        html_content += f"<div class='store-info-header'>"
        html_content += f"<h2>{store_name}</h2>"
        html_content += f"<p>NIT: {store_nit}</p>"
        html_content += f"<p>Tel/WhatsApp: {store_phone}</p>"
        html_content += "</div>"

        html_content += "<div class='invoice-title'><p>FACTURA DE VENTA</p></div>"
        html_content += f"<div class='date-time'><p>Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></div>"
        html_content += "<hr>"

        html_content += "<table>"
        html_content += "<tr><th>Producto</th><th>Cant.</th><th>P.Unit</th><th>Subtotal</th></tr>" # Cabeceras más cortas

        for item_data in items:
            product_name, quantity, unit_price, subtotal = item_data
            # Formato de precios sin símbolo de moneda, ya que el CSS puede ser más pequeño
            html_content += f"<tr><td>{product_name}</td><td class='text-right'>{quantity}</td><td class='text-right'>{unit_price:.2f}</td><td class='text-right'>{subtotal:.2f}</td></tr>"
        
        html_content += "</table>"

        # Línea antes de los totales
        html_content += "<hr style='border-top: 1px solid #000;'>" # Línea sólida antes de totales

        html_content += "<table class='total-section'>"
        html_content += f"<tr><td colspan='3'><strong>TOTAL:</strong></td><td class='text-right'><strong>{total_sale:.2f}</strong></td></tr>"
        html_content += f"<tr><td colspan='3'>Paga con:</td><td class='text-right'>{paid_amount:.2f}</td></tr>"
        html_content += f"<tr><td colspan='3'>Cambio:</td><td class='text-right'>{change_amount:.2f}</td></tr>"
        html_content += "</table>"
        html_content += "<hr>"
        html_content += "<div class='footer-message'><p>¡Gracias por su compra!</p></div>"
        html_content += "</body></html>"

        doc.setHtml(html_content)
        
        # Para depuración con PDF (descomenta para probar el formato)
        # printer_debug_pdf = QPrinter(QPrinter.HighResolution)
        # printer_debug_pdf.setPageLayout(page_layout)
        # printer_debug_pdf.setOutputFormat(QPrinter.PdfFormat)
        # printer_debug_pdf.setOutputFileName("factura_sin_logo_debug.pdf")
        # doc.print_(printer_debug_pdf)
        # print("PDF de depuración (sin logo) generado.")

        doc.print_(printer)

        if printer.printerState() == QPrinter.Error:
            error_message = f"No se pudo imprimir la factura. Estado de la impresora: {printer.printerState()}."
            QMessageBox.critical(None, "Error de Impresión", error_message)
            print(error_message)
            return False
        
        return True