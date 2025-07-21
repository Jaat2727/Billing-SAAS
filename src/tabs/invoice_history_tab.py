# src/tabs/invoice_history_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QPushButton, QHBoxLayout, QComboBox, QMessageBox)
from src.utils.database import SessionLocal
from src.models import Invoice, UserSettings
from src.utils.theme import DARK_THEME
from src.utils.pdf_service import PdfService

from src.tabs.base_tab import BaseTab

class InvoiceHistoryTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.db_session = self.get_db_session()
        self.init_ui()
        self.load_invoices()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(6)
        self.invoice_table.setHorizontalHeaderLabels(["Invoice #", "Company", "Date", "Total", "Status", "Actions"])
        self.invoice_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        main_layout.addWidget(self.invoice_table)

    def load_invoices(self):
        self.invoice_table.setRowCount(0)
        invoices = self.db_session.query(Invoice).order_by(Invoice.invoice_date.desc()).all()
        for inv in invoices:
            row = self.invoice_table.rowCount()
            self.invoice_table.insertRow(row)
            self.invoice_table.setItem(row, 0, QTableWidgetItem(inv.invoice_number))
            self.invoice_table.setItem(row, 1, QTableWidgetItem(inv.customer.name))
            self.invoice_table.setItem(row, 2, QTableWidgetItem(inv.invoice_date.strftime("%Y-%m-%d")))
            self.invoice_table.setItem(row, 3, QTableWidgetItem(f"₹{inv.total_amount:,.2f}"))

            status_combo = QComboBox()
            status_combo.addItems(["Pending", "Paid", "Overdue"])
            status_combo.setCurrentText(inv.payment_status)
            # status_combo.currentTextChanged.connect(lambda text, inv_id=inv.id: self.update_status(text, inv_id))
            self.invoice_table.setCellWidget(row, 4, status_combo)

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            download_btn = QPushButton("Download PDF")
            download_btn.clicked.connect(lambda chk, inv=inv: self.redownload_invoice(inv))
            share_btn = QPushButton("Share")
            share_btn.clicked.connect(lambda chk, inv=inv: self.share_invoice(inv))
            actions_layout.addWidget(download_btn)
            actions_layout.addWidget(share_btn)
            actions_layout.setContentsMargins(0,0,0,0)
            self.invoice_table.setCellWidget(row, 5, actions_widget)

    def redownload_invoice(self, invoice):
        settings = self.db_session.query(UserSettings).first()
        if not settings:
            QMessageBox.critical(self, "Error", "Please configure your company settings first.")
            return

        items = []
        for item in invoice.items:
            items.append({
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price_per_unit": item.price_per_unit
            })

        invoice_data = {
            "invoice_number": invoice.invoice_number,
            "date": invoice.date.strftime("%Y-%m-%d"),
            "vehicle_number": invoice.vehicle_number,
            "customer": {
                "name": invoice.customer.name,
                "address": invoice.customer.address,
                "gstin": invoice.customer.gstin,
                "state_code": invoice.customer.state_code
            },
            "items": items
        }

        pdf_service = PdfService(settings)
        file_name = pdf_service.generate_invoice(invoice_data)
        QMessageBox.information(self, "Success", f"Invoice PDF re-downloaded and saved as {file_name}")

    def share_invoice(self, invoice):
        settings = self.db_session.query(UserSettings).first()
        if not settings:
            QMessageBox.critical(self, "Error", "Please configure your company settings first.")
            return

        items = []
        for item in invoice.items:
            items.append({
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price_per_unit": item.price_per_unit
            })

        invoice_data = {
            "invoice_number": invoice.invoice_number,
            "date": invoice.date.strftime("%Y-%m-%d"),
            "vehicle_number": invoice.vehicle_number,
            "customer": {
                "name": invoice.customer.name,
                "address": invoice.customer.address,
                "gstin": invoice.customer.gstin,
                "state_code": invoice.customer.state_code
            },
            "items": items
        }

        pdf_service = PdfService(settings)
        file_name = pdf_service.generate_invoice(invoice_data)

        try:
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_name))
        except ImportError:
            QMessageBox.critical(self, "Error", "Could not open file. PySide6 is required for this feature.")


    def apply_styles(self):
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {DARK_THEME['bg_surface']};
                gridline-color: {DARK_THEME['border_main']};
                border: 1px solid {DARK_THEME['border_main']};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background-color: {DARK_THEME['bg_sidebar']};
                color: {DARK_THEME['text_secondary']};
                padding: 10px;
                border: none;
            }}
            QTableWidget::item {{
                padding: 10px;
                color: {DARK_THEME['text_primary']};
            }}
        """)
