from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from datetime import datetime, timedelta
import os

def generate_license_pdf(license_data, output_path):
    """Generate a PDF fishing license with official styling."""
    
    # Initialize the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#1a5f7a')
    ))
    
    styles.add(ParagraphStyle(
        name='OfficialStamp',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        textColor=colors.HexColor('#1a5f7a')
    ))
    
    # Content elements
    elements = []
    
    # Header with Coat of Arms
    current_dir = os.path.dirname(os.path.abspath(__file__))
    coat_of_arms_path = os.path.join(current_dir, '..', 'static', 'images', 'malawi-coat-of-arms.svg')
    if os.path.exists(coat_of_arms_path):
        img = Image(coat_of_arms_path, width=2*inch, height=2*inch)
        elements.append(img)
    
    # Title
    elements.append(Paragraph(
        'REPUBLIC OF MALAWI<br/>HUNTING AND FISHING LICENSE',
        styles['CustomTitle']
    ))
    
    # License Details
    license_info = [
        ['License Number:', license_data.get('license_number', '')],
        ['License Holder:', license_data.get('full_name', '')],
        ['National ID/Passport:', license_data.get('id_number', '')],
        ['License Type:', 'Fishing License'],
        ['Fishing Zone:', license_data.get('fishing_zone', '')],
        ['Duration:', f"{license_data.get('duration', '')} months"],
        ['Issue Date:', datetime.now().strftime('%d-%m-%Y')],
        ['Expiry Date:', (datetime.now() + timedelta(days=int(license_data.get('duration', 1)) * 30)).strftime('%d-%m-%Y')],
        ['Payment Status:', 'PAID'],
        ['Payment Reference:', license_data.get('payment_reference', '')]
    ]
    
    # Create and style the table
    table = Table(license_info, colWidths=[2.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (-1, -1), colors.white),
        ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
    ]))
    
    elements.append(Spacer(1, 20))
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Official Stamp
    elements.append(Spacer(1, 30))
    stamp_canvas = Canvas(None)
    stamp_canvas.setFillColor(colors.HexColor('#1a5f7a'))
    stamp_canvas.setStrokeColor(colors.HexColor('#1a5f7a'))
    
    # Create circular stamp
    stamp = Drawing(150, 150)
    circle = Circle(75, 75, 70)
    circle.strokeColor = colors.HexColor('#1a5f7a')
    circle.strokeWidth = 2
    circle.fillColor = None
    stamp.add(circle)
    
    # Add inner circle
    inner_circle = Circle(75, 75, 65)
    inner_circle.strokeColor = colors.HexColor('#1a5f7a')
    inner_circle.strokeWidth = 1
    inner_circle.fillColor = None
    stamp.add(inner_circle)
    
    elements.append(stamp)
    
    # Stamp Text
    elements.append(Paragraph(
        'DEPARTMENT OF FISHERIES<br/>REPUBLIC OF MALAWI<br/>OFFICIAL LICENSE',
        styles['OfficialStamp']
    ))
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        '<para alignment="center"><b>OFFICIAL DOCUMENT - VOID IF ALTERED</b></para>',
        styles['Heading2']
    ))
    
    # QR Code for verification
    qr = QrCodeWidget(f"License Verification: {license_data.get('license_number', '')}")
    qr_drawing = Drawing(1.5*inch, 1.5*inch)
    qr_drawing.add(qr)
    elements.append(qr_drawing)
    
    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        '<para alignment="center">Approved by the Department of Fisheries, Malawi</para>',
        styles['Normal']
    ))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        '<para alignment="center">System created by Emmanuel Magalasi</para>',
        styles['Normal']
    ))
    
    # Build the PDF
    doc.build(elements)
    
    return output_path