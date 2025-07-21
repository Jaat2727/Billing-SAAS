# src/tabs/create_invoice_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QDateEdit)
from PyQt6.QtCore import QDate

from src.utils.database import SessionLocal
from src.models import CustomerCompany, Product
from src.utils.theme import DARK_THEME

class CreateInvoiceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db_session = SessionLocal()
        self.init_ui()
        self.apply_styles()
        self.load_initial_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Top Section: Customer and Invoice Details
        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)

        # Customer Details
        customer_group = QFrame()
        customer_group.setObjectName("form-group")
        customer_layout = QVBoxLayout(customer_group)
        customer_layout.addWidget(QLabel("Select Customer Company"))
        self.company_combo = QComboBox()
        self.company_combo.currentIndexChanged.connect(self.on_company_selected)
        customer_layout.addWidget(self.company_combo)
        top_layout.addWidget(customer_group, 1)

        # Invoice Details
        invoice_details_group = QFrame()
        invoice_details_group.setObjectName("form-group")
        invoice_details_layout = QGridLayout(invoice_details_group)
        self.invoice_date_edit = QDateEdit(QDate.currentDate())
        self.vehicle_no_input = QLineEdit()
        self.state_combo = QComboBox() # For GST state selection
        invoice_details_layout.addWidget(QLabel("Invoice Date:"), 0, 0)
        invoice_details_layout.addWidget(self.invoice_date_edit, 0, 1)
        invoice_details_layout.addWidget(QLabel("Vehicle Number:"), 1, 0)
        invoice_details_layout.addWidget(self.vehicle_no_input, 1, 1)
        invoice_details_layout.addWidget(QLabel("State for GST:"), 2, 0)
        invoice_details_layout.addWidget(self.state_combo, 2, 1)
        top_layout.addWidget(invoice_details_group, 1)

        main_layout.addWidget(top_frame)

        # Middle Section: Add Products
        add_product_frame = QFrame()
        add_product_layout = QHBoxLayout(add_product_frame)
        self.product_combo = QComboBox()
        self.quantity_input = QLineEdit("1")
        add_product_btn = QPushButton("Add Product to Invoice")
        add_product_btn.clicked.connect(self.add_product_to_table)
        add_product_layout.addWidget(self.product_combo, 2)
        add_product_layout.addWidget(self.quantity_input, 1)
        add_product_layout.addWidget(add_product_btn, 1)
        main_layout.addWidget(add_product_frame)

        # Items Table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Product Name", "Price", "Quantity", "Total", ""])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.items_table)

        # Bottom Section: Total and Generate PDF
        bottom_layout = QHBoxLayout()
        self.total_label = QLabel("Total Amount: ₹0.00")
        self.total_label.setObjectName("total-label")
        generate_pdf_btn = QPushButton("Generate & Save Invoice PDF")
        generate_pdf_btn.setObjectName("primary-button")
        generate_pdf_btn.clicked.connect(self.generate_invoice_pdf)
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(generate_pdf_btn)
        main_layout.addLayout(bottom_layout)

    def load_initial_data(self):
        # Load companies
        companies = self.db_session.query(CustomerCompany).all()
        for company in companies:
            self.company_combo.addItem(company.name, company.id)

        # Load states for GST
        from src.utils.constants import INDIAN_STATES
        for state in INDIAN_STATES:
            self.state_combo.addItem(state['name'], state['code'])

    def on_company_selected(self, index):
        company_id = self.company_combo.itemData(index)
        if company_id:
            company = self.db_session.query(CustomerCompany).get(company_id)
            self.product_combo.clear()
            for product in company.products:
                self.product_combo.addItem(product.name, product.id)

    def add_product_to_table(self):
        product_id = self.product_combo.itemData(self.product_combo.currentIndex())
        if not product_id: return

        product = self.db_session.query(Product).get(product_id)
        quantity = int(self.quantity_input.text())
        total_price = product.price * quantity

        row_position = self.items_table.rowCount()
        self.items_table.insertRow(row_position)

        self.items_table.setItem(row_position, 0, QTableWidgetItem(product.name))
        self.items_table.setItem(row_position, 1, QTableWidgetItem(f"₹{product.price:,.2f}"))
        self.items_table.setItem(row_position, 2, QTableWidgetItem(str(quantity)))
        self.items_table.setItem(row_position, 3, QTableWidgetItem(f"₹{total_price:,.2f}"))

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self.items_table.removeRow(row_position))
        self.items_table.setCellWidget(row_position, 4, remove_btn)

        self.update_total()

    def update_total(self):
        total = 0
        for row in range(self.items_table.rowCount()):
            total += float(self.items_table.item(row, 3).text().replace("₹", "").replace(",", ""))
        self.total_label.setText(f"Total Amount: ₹{total:,.2f}")

    def generate_invoice_pdf(self):
        # ... PDF generation logic will go here ...
        QMessageBox.information(self, "Success", "Invoice PDF generated and saved (placeholder).")

    def apply_styles(self):
        self.setStyleSheet(f"""
            QFrame#form-group {{
                background-color: {DARK_THEME['bg_surface']};
                border-radius: 8px;
                padding: 15px;
            }}
            QLabel, QDateEdit {{ color: {DARK_THEME['text_primary']}; }}
            QLineEdit, QComboBox {{
                background-color: {DARK_THEME['bg_input']};
                color: {DARK_THEME['text_primary']};
                border: 1px solid {DARK_THEME['border_main']};
                border-radius: 6px;
                padding: 8px;
            }}
            QTableWidget {{
                background-color: {DARK_THEME['bg_surface']};
                gridline-color: {DARK_THEME['border_main']};
                border: 1px solid {DARK_THEME['border_main']};
            }}
            QHeaderView::section {{
                background-color: {DARK_THEME['bg_sidebar']};
                color: {DARK_THEME['text_secondary']};
                padding: 10px;
                border: none;
            }}
            QLabel#total-label {{
                font-size: 18px;
                font-weight: 600;
                color: {DARK_THEME['text_primary']};
            }}
            QPushButton#primary-button {{
                background-color: {DARK_THEME['accent_primary']};
                color: {DARK_THEME['text_on_accent']};
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }}
        """)
