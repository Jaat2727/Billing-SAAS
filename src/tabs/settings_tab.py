# src/tabs/settings_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QGridLayout, QFrame, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
from src.utils.theme import APP_THEME
from src.utils.database import SessionLocal
from src.models.user import UserSettings
from src.utils.helpers import log_action

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db_session = SessionLocal()
        self.init_ui()
        self.load_settings()
        self.apply_styles()

    def init_ui(self):
        # --- Main Layout: A horizontal layout for columns ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Left Column ---
        left_column_layout = QVBoxLayout()
        left_column_layout.setSpacing(25)
        
        # --- Company Profile Card ---
        company_card = QFrame(self)
        company_card.setObjectName("content-card")
        company_layout = QVBoxLayout(company_card)
        company_layout.setSpacing(20)
        
        company_title = QLabel("Company Profile")
        company_title.setObjectName("card-title")
        company_subtitle = QLabel("This information will appear on your invoices.")
        company_subtitle.setObjectName("card-subtitle")
        company_layout.addWidget(company_title)
        company_layout.addWidget(company_subtitle)
        
        company_form_layout = QGridLayout()
        company_form_layout.setHorizontalSpacing(20)
        company_form_layout.setVerticalSpacing(15)
        
        self.company_name_input = QLineEdit()
        self.gstin_input = QLineEdit()
        self.pan_input = QLineEdit()
        self.address_input = QLineEdit() # Added address for completeness
        
        company_form_layout.addWidget(QLabel("Legal Company Name"), 0, 0)
        company_form_layout.addWidget(self.company_name_input, 0, 1)
        company_form_layout.addWidget(QLabel("GSTIN"), 1, 0)
        company_form_layout.addWidget(self.gstin_input, 1, 1)
        company_form_layout.addWidget(QLabel("PAN Number"), 2, 0)
        company_form_layout.addWidget(self.pan_input, 2, 1)
        company_form_layout.addWidget(QLabel("Company Address"), 3, 0)
        company_form_layout.addWidget(self.address_input, 3, 1)
        company_layout.addLayout(company_form_layout)
        
        left_column_layout.addWidget(company_card)
        left_column_layout.addStretch()

        # --- Right Column ---
        right_column_layout = QVBoxLayout()
        right_column_layout.setSpacing(25)

        # --- Contact & Payment Card ---
        contact_card = QFrame(self)
        contact_card.setObjectName("content-card")
        contact_layout = QVBoxLayout(contact_card)
        contact_layout.setSpacing(20)

        contact_title = QLabel("Contact & Payment Details")
        contact_title.setObjectName("card-title")
        contact_subtitle = QLabel("Contact and UPI details for your clients.")
        contact_subtitle.setObjectName("card-subtitle")
        contact_layout.addWidget(contact_title)
        contact_layout.addWidget(contact_subtitle)

        contact_form_layout = QGridLayout()
        contact_form_layout.setHorizontalSpacing(20)
        contact_form_layout.setVerticalSpacing(15)

        self.mobile_input = QLineEdit()
        self.email_input = QLineEdit()
        self.upi_id_input = QLineEdit()

        contact_form_layout.addWidget(QLabel("Mobile Number"), 0, 0)
        contact_form_layout.addWidget(self.mobile_input, 0, 1)
        contact_form_layout.addWidget(QLabel("Email Address"), 1, 0)
        contact_form_layout.addWidget(self.email_input, 1, 1)
        contact_form_layout.addWidget(QLabel("UPI ID (for payments)"), 2, 0)
        contact_form_layout.addWidget(self.upi_id_input, 2, 1)
        contact_layout.addLayout(contact_form_layout)

        # --- Invoice Customization Card ---
        invoice_card = QFrame(self)
        invoice_card.setObjectName("content-card")
        invoice_layout = QVBoxLayout(invoice_card)
        invoice_layout.setSpacing(20)

        invoice_title = QLabel("Invoice Customization")
        invoice_title.setObjectName("card-title")
        invoice_subtitle = QLabel("Add a custom message to your invoices.")
        invoice_subtitle.setObjectName("card-subtitle")
        invoice_layout.addWidget(invoice_title)
        invoice_layout.addWidget(invoice_subtitle)

        self.tagline_input = QLineEdit()
        self.tagline_input.setPlaceholderText("e.g., Thank you for your business!")
        invoice_layout.addWidget(QLabel("Invoice Tagline / Footer Note"))
        invoice_layout.addWidget(self.tagline_input)
        
        right_column_layout.addWidget(contact_card)
        right_column_layout.addWidget(invoice_card)
        right_column_layout.addStretch()
        
        # --- Save Button at the bottom ---
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.save_button = QPushButton("Save All Changes")
        self.save_button.setObjectName("primary-button")
        self.save_button.setFixedSize(180, 44)
        self.save_button.clicked.connect(self.save_settings)
        save_layout.addWidget(self.save_button)

        # --- Assemble Main Layout ---
        main_body_layout = QHBoxLayout()
        main_body_layout.addLayout(left_column_layout, 1)
        main_body_layout.addLayout(right_column_layout, 1)
        
        main_layout.addLayout(main_body_layout, 1)
        main_layout.addLayout(save_layout)

    def load_settings(self):
        settings = self.db_session.query(UserSettings).first()
        if settings:
            self.company_name_input.setText(settings.company_name or "")
            self.gstin_input.setText(settings.gstin or "")
            self.pan_input.setText(settings.pan_number or "")
            # Assuming address is a new field, need to add to UserSettings model
            # self.address_input.setText(settings.address or "")
            self.mobile_input.setText(settings.mobile_number or "")
            self.email_input.setText(settings.email or "")
            self.upi_id_input.setText(settings.upi_id or "")
            self.tagline_input.setText(settings.tagline or "")

    def save_settings(self):
        settings = self.db_session.query(UserSettings).first()
        if settings:
            details = "Updated company settings."
            settings.company_name = self.company_name_input.text()
            settings.gstin = self.gstin_input.text()
            settings.pan_number = self.pan_input.text()
            # settings.address = self.address_input.text()
            settings.mobile_number = self.mobile_input.text()
            settings.email = self.email_input.text()
            settings.upi_id = self.upi_id_input.text()
            settings.tagline = self.tagline_input.text()
            
            log_action(self.db_session, "UPDATE", "Settings", settings.id, details)
            self.db_session.commit()
            
            # --- DEFINITIVE FEEDBACK ---
            msg_box = QMessageBox(self)
            msg_box.setText("Settings have been saved successfully.")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Success")
            msg_box.setStyleSheet(f"""
                QMessageBox {{ background-color: {APP_THEME['bg_content']}; }}
                QLabel {{ color: {APP_THEME['text_primary']}; }}
                QPushButton {{ background-color: {APP_THEME['accent_blue']}; color: {APP_THEME['text_white']}; padding: 8px 16px; border-radius: 4px; border: none; }}
            """)
            msg_box.exec()

    def apply_styles(self):
        self.setStyleSheet(f"""
            SettingsTab {{ font-family: Roboto; }}
            QFrame#content-card {{
                background-color: {APP_THEME['bg_content']};
                border: 1px solid {APP_THEME['border']};
                border-radius: 8px;
                padding: 20px;
            }}
            QLabel#card-title {{
                font-size: 18px;
                font-weight: 600;
                color: {APP_THEME['text_primary']};
                padding-bottom: 5px;
            }}
            QLabel#card-subtitle {{
                font-size: 13px;
                color: {APP_THEME['text_secondary']};
                padding-bottom: 10px;
            }}
            QPushButton#primary-button {{
                background-color: {APP_THEME['accent_blue']};
                color: {APP_THEME['text_white']};
                border: none; border-radius: 6px; padding: 10px; font-weight: 600;
            }}
            QPushButton#primary-button:hover {{
                background-color: {APP_THEME['accent_blue_hover']};
            }}
        """)
