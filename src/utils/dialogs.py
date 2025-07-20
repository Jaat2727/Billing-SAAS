# src/utils/dialogs.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
                             QComboBox, QDialogButtonBox, QDoubleSpinBox, QSpinBox, QPushButton)
from src.utils.theme import APP_THEME

# ... (INDIAN_STATES list remains the same, ensure it's here) ...
INDIAN_STATES = [
    {"name": "Andhra Pradesh", "code": "37"}, {"name": "Arunachal Pradesh", "code": "12"},
    {"name": "Assam", "code": "18"}, {"name": "Bihar", "code": "10"}, {"name": "Chhattisgarh", "code": "22"},
    {"name": "Goa", "code": "30"}, {"name": "Gujarat", "code": "24"}, {"name": "Haryana", "code": "06"},
    {"name": "Himachal Pradesh", "code": "02"}, {"name": "Jharkhand", "code": "20"},
    {"name": "Karnataka", "code": "29"}, {"name": "Kerala", "code": "32"},
    {"name": "Madhya Pradesh", "code": "23"}, {"name": "Maharashtra", "code": "27"},
    {"name": "Manipur", "code": "14"}, {"name": "Meghalaya", "code": "17"},
    {"name": "Mizoram", "code": "15"}, {"name": "Nagaland", "code": "13"},
    {"name": "Odisha", "code": "21"}, {"name": "Punjab", "code": "03"},
    {"name": "Rajasthan", "code": "08"}, {"name": "Sikkim", "code": "11"},
    {"name": "Tamil Nadu", "code": "33"}, {"name": "Telangana", "code": "36"},
    {"name": "Tripura", "code": "16"}, {"name": "Uttar Pradesh", "code": "09"},
    {"name": "Uttarakhand", "code": "05"}, {"name": "West Bengal", "code": "19"},
    {"name": "Andaman and Nicobar Islands", "code": "35"}, {"name": "Chandigarh", "code": "04"},
    {"name": "Dadra and Nagar Haveli and Daman and Diu", "code": "26"}, {"name": "Delhi", "code": "07"},
    {"name": "Jammu and Kashmir", "code": "01"}, {"name": "Ladakh", "code": "38"},
    {"name": "Lakshadweep", "code": "31"}, {"name": "Puducherry", "code": "34"}
]


class BaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {APP_THEME['bg_content']}; border: 1px solid {APP_THEME['border']}; font-family: Roboto; }}
            QLabel {{ color: {APP_THEME['text_secondary']}; font-size: 13px; font-weight: 500; }}
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {{
                background-color: {APP_THEME['bg_content']};
                color: {APP_THEME['text_primary']};
                border: 1px solid {APP_THEME['input_border']};
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
                border: 1px solid {APP_THEME['input_border_focus']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: {APP_THEME['input_border']};
                border-left-style: solid;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QComboBox::down-arrow {{
                image: url(resources/icons/chevron-down.svg);
                width: 12px;
                height: 12px;
            }}
        """)

class CompanyDialog(BaseDialog):
    def __init__(self, company=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Company Details" if company else "Add New Company")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        title = QLabel(self.windowTitle())
        title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {APP_THEME['text_primary']};")
        main_layout.addWidget(title)

        layout = QGridLayout()
        layout.setSpacing(15)

        self.name_input = QLineEdit(company.name if company else "")
        self.gstin_input = QLineEdit(company.gstin if company else "")
        self.gstin_input.setMaxLength(15)
        self.address_input = QLineEdit(company.address if company else "")
        self.state_combo = QComboBox()

        current_state_index = 0
        for i, state in enumerate(INDIAN_STATES):
            self.state_combo.addItem(f"{state['name']} ({state['code']})", state)
            if company and company.state == state['name']:
                current_state_index = i
        self.state_combo.setCurrentIndex(current_state_index)

        layout.addWidget(QLabel("Company Name:"), 0, 0); layout.addWidget(self.name_input, 0, 1)
        layout.addWidget(QLabel("GSTIN:"), 1, 0); layout.addWidget(self.gstin_input, 1, 1)
        layout.addWidget(QLabel("State:"), 2, 0); layout.addWidget(self.state_combo, 2, 1)
        layout.addWidget(QLabel("Address:"), 3, 0); layout.addWidget(self.address_input, 3, 1)
        main_layout.addLayout(layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Save Changes" if company else "Add Company")
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {APP_THEME['accent_blue']}; color: {APP_THEME['text_white']};
                border: none; border-radius: 6px; padding: 10px 20px; font-weight: 600; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {APP_THEME['accent_blue_hover']}; }}
        """)

        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {APP_THEME['bg_main']}; color: {APP_THEME['text_secondary']};
                border: 1px solid {APP_THEME['border']}; border-radius: 6px; padding: 10px 20px; font-weight: 500; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {APP_THEME['border']}; }}
        """)
        main_layout.addWidget(buttons)

    def get_data(self):
        selected_state = self.state_combo.currentData()
        return {
            "name": self.name_input.text().strip(),
            "gstin": self.gstin_input.text().strip().upper(),
            "state": selected_state['name'],
            "state_code": selected_state['code'],
            "address": self.address_input.text().strip()
        }

class ProductDialog(BaseDialog):
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Product" if product else "Add New Product")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        title = QLabel(self.windowTitle())
        title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {APP_THEME['text_primary']};")
        main_layout.addWidget(title)

        layout = QGridLayout()
        layout.setSpacing(15)

        self.name_input = QLineEdit(product.name if product else "")
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1_000_000_000)
        self.price_input.setValue(product.price if product else 0)
        self.price_input.setPrefix("₹ ")
        self.price_input.setDecimals(2)
        self.price_input.setSingleStep(50)

        layout.addWidget(QLabel("Product Name:"), 0, 0); layout.addWidget(self.name_input, 0, 1)
        layout.addWidget(QLabel("Price:"), 1, 0); layout.addWidget(self.price_input, 1, 1)
        main_layout.addLayout(layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Save Changes" if product else "Add Product")
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {APP_THEME['accent_blue']}; color: {APP_THEME['text_white']};
                border: none; border-radius: 6px; padding: 10px 20px; font-weight: 600; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {APP_THEME['accent_blue_hover']}; }}
        """)

        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {APP_THEME['bg_main']}; color: {APP_THEME['text_secondary']};
                border: 1px solid {APP_THEME['border']}; border-radius: 6px; padding: 10px 20px; font-weight: 500; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {APP_THEME['border']}; }}
        """)
        main_layout.addWidget(buttons)

    def get_data(self):
        return {"name": self.name_input.text().strip(), "price": self.price_input.value()}

class StockAdjustmentDialog(BaseDialog):
    def __init__(self, product_name, current_stock, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Adjust Stock: {product_name}")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        title = QLabel(self.windowTitle())
        title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {APP_THEME['text_primary']};")
        main_layout.addWidget(title)

        layout = QGridLayout()
        layout.setSpacing(15)

        layout.addWidget(QLabel(f"Current Stock: <b>{current_stock}</b>"), 0, 0, 1, 2)

        self.adjustment_input = QSpinBox()
        self.adjustment_input.setRange(-100000, 100000)
        self.adjustment_input.setPrefix("Adjustment: ")

        self.reason_input = QLineEdit("Manual stock adjustment")

        layout.addWidget(QLabel("Change Quantity:"), 1, 0); layout.addWidget(self.adjustment_input, 1, 1)
        layout.addWidget(QLabel("Reason for change:"), 2, 0); layout.addWidget(self.reason_input, 2, 1)
        main_layout.addLayout(layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Apply Adjustment")
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {APP_THEME['accent_blue']}; color: {APP_THEME['text_white']};
                border: none; border-radius: 6px; padding: 10px 20px; font-weight: 600; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {APP_THEME['accent_blue_hover']}; }}
        """)

        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {APP_THEME['bg_main']}; color: {APP_THEME['text_secondary']};
                border: 1px solid {APP_THEME['border']}; border-radius: 6px; padding: 10px 20px; font-weight: 500; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {APP_THEME['border']}; }}
        """)
        main_layout.addWidget(buttons)

    def get_data(self):
        return {
            "adjustment": self.adjustment_input.value(),
            "reason": self.reason_input.text().strip()
        }
