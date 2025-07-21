# src/utils/invoice_template.py
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors

class InvoiceTemplate:
    def __init__(self, canvas, width, height, settings):
        self.c = canvas
        self.width = width
        self.height = height
        self.settings = settings

    def draw_invoice(self, invoice_data):
        self.draw_header()
        self.draw_customer_info(invoice_data)
        self.draw_invoice_details(invoice_data)
        self.draw_items_table(invoice_data)
        self.draw_summary(invoice_data)
        self.draw_footer()

    def draw_header(self):
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawString(50, 750, self.settings.company_name)
        self.c.setFont("Helvetica", 12)
        self.c.drawString(50, 730, self.settings.address)
        self.c.drawString(50, 715, f"GSTIN: {self.settings.gstin}")
        self.c.drawString(50, 700, f"PAN: {self.settings.pan_number}")
        self.c.drawString(50, 685, f"Email: {self.settings.email}")
        self.c.drawString(50, 670, f"UPI ID: {self.settings.upi_id}")

    def draw_customer_info(self, invoice_data):
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(350, 750, "Bill To:")
        self.c.setFont("Helvetica", 12)
        self.c.drawString(350, 730, invoice_data['customer']['name'])
        self.c.drawString(350, 715, invoice_data['customer']['address'])
        self.c.drawString(350, 700, f"GSTIN: {invoice_data['customer']['gstin']}")

    def draw_invoice_details(self, invoice_data):
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(50, 630, f"Invoice Number: {invoice_data['invoice_number']}")
        self.c.drawString(50, 615, f"Invoice Date: {invoice_data['date']}")
        self.c.drawString(50, 600, f"Vehicle Number: {invoice_data['vehicle_number']}")

    def draw_items_table(self, invoice_data):
        table_data = [["#", "Product", "Quantity", "Price", "Total"]]
        for i, item in enumerate(invoice_data['items']):
            table_data.append([
                str(i + 1),
                item['product_name'],
                str(item['quantity']),
                f"₹{item['price_per_unit']:.2f}",
                f"₹{item['quantity'] * item['price_per_unit']:.2f}"
            ])

        table = Table(table_data, colWidths=[30, 250, 70, 70, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        table.wrapOn(self.c, self.width, self.height)
        table.drawOn(self.c, 50, 450)

    def get_tax_info(self, subtotal, customer_state_code):
        if customer_state_code == self.settings.state_code:
            cgst = subtotal * 0.09
            sgst = subtotal * 0.09
            return {
                "tax_type": "CGST/SGST",
                "cgst": cgst,
                "sgst": sgst,
                "total_tax": cgst + sgst,
            }
        else:
            igst = subtotal * 0.18
            return {
                "tax_type": "IGST",
                "igst": igst,
                "total_tax": igst,
            }

    def draw_summary(self, invoice_data):
        subtotal = sum(item['quantity'] * item['price_per_unit'] for item in invoice_data['items'])
        tax_info = self.get_tax_info(subtotal, invoice_data['customer']['state_code'])
        total = subtotal + tax_info['total_tax']

        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(400, 400, "Subtotal:")
        if tax_info['tax_type'] == 'IGST':
            self.c.drawString(400, 380, "IGST (18%):")
        else:
            self.c.drawString(400, 380, "CGST (9%):")
            self.c.drawString(400, 360, "SGST (9%):")
        self.c.drawString(400, 340, "Total:")

        self.c.setFont("Helvetica", 12)
        self.c.drawString(500, 400, f"₹{subtotal:.2f}")
        if tax_info['tax_type'] == 'IGST':
            self.c.drawString(500, 380, f"₹{tax_info['igst']:.2f}")
        else:
            self.c.drawString(500, 380, f"₹{tax_info['cgst']:.2f}")
            self.c.drawString(500, 360, f"₹{tax_info['sgst']:.2f}")
        self.c.drawString(500, 340, f"₹{total:.2f}")

    def draw_footer(self):
        self.c.setFont("Helvetica-Oblique", 10)
        self.c.drawString(50, 100, self.settings.tagline)
