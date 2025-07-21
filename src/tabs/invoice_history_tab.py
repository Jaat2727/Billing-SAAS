# src/tabs/invoice_history_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QPushButton, QHBoxLayout, QComboBox)
from src.utils.database import SessionLocal
from src.models import Invoice
from src.utils.theme import DARK_THEME

class InvoiceHistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db_session = SessionLocal()
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
            share_btn = QPushButton("Share")
            actions_layout.addWidget(download_btn)
            actions_layout.addWidget(share_btn)
            actions_layout.setContentsMargins(0,0,0,0)
            self.invoice_table.setCellWidget(row, 5, actions_widget)

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
