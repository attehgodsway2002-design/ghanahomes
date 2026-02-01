from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import os
from datetime import datetime
from io import BytesIO

def generate_payment_receipt(payment):
    """Generate a PDF receipt for a payment"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20
    ))

    # Add company logo/header
    elements.append(Paragraph("GhanaHomes", styles['CustomTitle']))
    elements.append(Paragraph("Payment Receipt", styles['SubTitle']))
    elements.append(Spacer(1, 20))

    # Payment Details
    payment_data = [
        ['Receipt No:', f'GH-{payment.id}'],
        ['Date:', payment.updated_at.strftime('%B %d, %Y')],
        ['Time:', payment.updated_at.strftime('%I:%M %p')],
        ['Reference:', payment.paystack_reference],
        ['Status:', 'Paid'],
    ]

    # Customer Details
    customer_data = [
        ['Customer:', payment.user.get_full_name() or payment.user.username],
        ['Email:', payment.user.email],
        ['Phone:', payment.user.phone_number if hasattr(payment.user, 'phone_number') else 'N/A'],
    ]

    # Subscription Details
    subscription_data = [
        ['Plan:', payment.subscription.plan.name],
        ['Duration:', payment.subscription.duration.title()],
        ['Start Date:', payment.subscription.start_date.strftime('%B %d, %Y')],
        ['End Date:', payment.subscription.end_date.strftime('%B %d, %Y')],
    ]

    # Create tables
    payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
    payment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    subscription_table = Table(subscription_data, colWidths=[2*inch, 4*inch])
    subscription_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    # Payment Summary
    summary_data = [
        ['Description', 'Amount'],
        [f'{payment.subscription.plan.name} Subscription', f'₵{payment.amount}'],
        ['Total', f'₵{payment.amount}'],
    ]

    summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
    ]))

    # Add sections to the document
    elements.append(Paragraph("Payment Details", styles['Heading3']))
    elements.append(payment_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Customer Information", styles['Heading3']))
    elements.append(customer_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Subscription Details", styles['Heading3']))
    elements.append(subscription_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Payment Summary", styles['Heading3']))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    # Add footer
    elements.append(Paragraph(
        "Thank you for your business!<br/>"
        "For any questions, please contact support@ghanahomes.com",
        styles['Normal']
    ))

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf