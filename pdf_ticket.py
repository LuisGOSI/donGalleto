from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os
from db import app

def generar_pdf_ticket(idVenta, productos, subtotal, descuento, total):
    try:
        # Configurar rutas
        tickets_dir = os.path.join(app.root_path, 'static', 'tickets')
        os.makedirs(tickets_dir, exist_ok=True)
        filename = f"ticket_{idVenta}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(tickets_dir, filename)
        
        # Crear documento PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            alignment=1,
            fontSize=16,
            spaceAfter=20
        )
        
        # Encabezado
        elements.append(Paragraph("Don Galleto - Ticket de Venta", title_style))
        elements.append(Paragraph(f"<b>N° Venta:</b> {idVenta}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Tabla de productos
        product_data = [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
        
        for producto in productos:
            nombre = producto['name']
            cantidad = producto['quantity']
            tipo = producto['type'].lower()
            precio = producto['price']

            if tipo == "unidad":
                cantidad_display = f"{cantidad} Unidad"
            elif tipo == "paquete 1kg":
                cantidad_display = f"{cantidad} paquete 1kg"
            elif tipo == "paquete 700gr":
                cantidad_display = f"{cantidad} paquete 700gr"
            elif tipo == "gramaje":
                cantidad_display = f"{cantidad} gramos"
            else:
                cantidad_display = f"{cantidad} {tipo}"

            product_data.append([
                nombre,
                cantidad_display,
                f"${precio:.2f}",
                f"${producto['subtotal']:.2f}"
            ])
        
        product_table = Table(product_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5D6D7E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F2F3F4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(product_table)
        elements.append(Spacer(1, 30))
        
        # Totales
        descuento_valor = (subtotal * descuento / 100)
        total_data = [
            ['Subtotal:', f"${subtotal:.2f}"],
            ['Descuento:', f"${descuento_valor:.2f} - ({descuento:.0f}%)"],
            ['Total:', f"${total:.2f}"]
        ]
        
        total_table = Table(total_data, colWidths=[4*inch, 2*inch])
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(total_table)
        
        # Pie de página
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("¡Gracias por su compra!", ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            alignment=1,
            fontSize=12,
            spaceBefore=20
        )))
        
        # Generar PDF
        doc.build(elements)
        
        return filepath
        
    except Exception as e:
        app.logger.error(f"Error al generar PDF: {str(e)}")
        return None
