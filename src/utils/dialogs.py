# src/utils/dialogs.py
from PyQt6.QtWidgets import (QDialog, QGridLayout, QLabel, QLineEdit,
                             QComboBox, QDialogButtonBox, QDoubleSpinBox, QSpinBox)
from src.utils.theme import DARK_THEME
from src.utils.constants import INDIAN_STATES


class BaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {DARK_THEME['bg_surface']}; border: 1px solid {DARK_THEME['border_main']}; font-family: Roboto; }}
            QLabel {{ color: {DARK_THEME['text_secondary']}; font-size: 13px; }}
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {{
                background-color: {DARK_THEME['bg_input']}; color: {DARK_THEME['text_primary']};
                border: 1px solid {DARK_THEME['border_main']}; border-radius: 4px; padding: 8px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {{ border: 1px solid {DARK_THEME['border_focus']}; }}
        """)

class CompanyDialog(BaseDialog):
    # --- This entire class is complete and correct from the previous version ---
    def __init__(self, company=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Company Details" if company else "Add New Company")
        self.setMinimumWidth(400)
        layout = QGridLayout(self)
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
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Save Changes" if company else "Add Company")
        ok_button.setStyleSheet(f"background-color: {DARK_THEME['accent_primary']}; color: {DARK_THEME['text_on_accent']}; border: none; border-radius: 4px; padding: 8px 16px; font-weight: 600;")
        layout.addWidget(buttons, 4, 0, 1, 2)
    def get_data(self):
        selected_state = self.state_combo.currentData()
        return {"name": self.name_input.text().strip(), "gstin": self.gstin_input.text().strip().upper(), "state": selected_state['name'], "state_code": selected_state['code'], "address": self.address_input.text().strip()}

class ProductDialog(BaseDialog):
    # --- This entire class is complete and correct from the previous version ---
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Product" if product else "Add New Product")
        self.setMinimumWidth(400)
        layout = QGridLayout(self)
        layout.setSpacing(15)
        self.name_input = QLineEdit(product.name if product else "")
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1_000_000_000); self.price_input.setValue(product.price if product else 0)
        self.price_input.setPrefix("₹ "); self.price_input.setDecimals(2); self.price_input.setSingleStep(50)
        layout.addWidget(QLabel("Product Name:"), 0, 0); layout.addWidget(self.name_input, 0, 1)
        layout.addWidget(QLabel("Price:"), 1, 0); layout.addWidget(self.price_input, 1, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Save Changes" if product else "Add Product")
        ok_button.setStyleSheet(f"background-color: {DARK_THEME['accent_primary']}; color: {DARK_THEME['text_on_accent']}; border: none; border-radius: 4px; padding: 8px 16px; font-weight: 600;")
        layout.addWidget(buttons, 2, 0, 1, 2)
    def get_data(self):
        return {"name": self.name_input.text().strip(), "price": self.price_input.value()}

class StockAdjustmentDialog(BaseDialog):
    # --- NEW: The fully functional stock adjustment dialog ---
    def __init__(self, product_name, current_stock, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Adjust Stock for {product_name}")
        layout = QGridLayout(self)
        layout.setSpacing(15)
        layout.addWidget(QLabel(f"Current Stock: {current_stock}"), 0, 0, 1, 2)
        self.adjustment_input = QSpinBox()
        self.adjustment_input.setRange(-100000, 100000)
        self.adjustment_input.setPrefix("Adjustment: ")
        self.reason_input = QLineEdit("Manual stock adjustment")
        layout.addWidget(QLabel("Change Quantity:"), 1, 0); layout.addWidget(self.adjustment_input, 1, 1)
        layout.addWidget(QLabel("Reason:"), 2, 0); layout.addWidget(self.reason_input, 2, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Apply Adjustment")
        ok_button.setStyleSheet(f"background-color: {DARK_THEME['accent_primary']}; color: {DARK_THEME['text_on_accent']}; border: none; border-radius: 4px; padding: 8px 16px; font-weight: 600;")
        layout.addWidget(buttons, 3, 0, 1, 2)
    def get_data(self):
        return {"adjustment": self.adjustment_input.value(), "reason": self.reason_input.text().strip()}