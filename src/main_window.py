import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QFileDialog, QMessageBox)
from PyQt.QtGui import QIcon

from src.utils.theme import DARK_THEME
from src.utils.csv_manager import CsvManager
from src.tabs.dashboard_tab import DashboardTab
from src.tabs.companies_products_tab import CompaniesProductsTab
from src.tabs.create_invoice_tab import CreateInvoiceTab
from src.tabs.invoice_history_tab import InvoiceHistoryTab
from src.tabs.inventory_tab import InventoryTab
from src.tabs.settings_tab import SettingsTab
from src.tabs.audit_log_tab import AuditLogTab

class SaaSBillingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BillTracker Pro")
        self.setGeometry(100, 100, 1440, 900)
        self.active_nav_button = None
        self.resource_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'resources')
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        nav_sidebar = self.create_nav_sidebar()
        main_layout.addWidget(nav_sidebar)

        right_area_widget = QWidget()
        right_area_layout = QVBoxLayout(right_area_widget)
        right_area_layout.setContentsMargins(0, 0, 0, 0)
        right_area_layout.setSpacing(0)
        main_layout.addWidget(right_area_widget, 1)

        top_header = self.create_top_header()
        right_area_layout.addWidget(top_header)

        self.stacked_widget = QStackedWidget()
        right_area_layout.addWidget(self.stacked_widget)
        
        self.companies_tab_instance = CompaniesProductsTab()
        self.inventory_tab_instance = InventoryTab()
        self.audit_log_tab_instance = AuditLogTab()
        
        self.invoice_history_tab_instance = InvoiceHistoryTab()
        self.csv_manager = CsvManager(
            self.companies_tab_instance,
            self.inventory_tab_instance,
            self.audit_log_tab_instance,
            self.invoice_history_tab_instance
        )

        self.tabs_map = {
            "Dashboard": DashboardTab(),
            "Companies & Products": self.companies_tab_instance,
            "Create Invoice": CreateInvoiceTab(),
            "Past Invoices": InvoiceHistoryTab(),
            "Inventory": self.inventory_tab_instance,
            "Audit Log": self.audit_log_tab_instance,
            "Settings": SettingsTab()
        }
        for widget in self.tabs_map.values():
            self.stacked_widget.addWidget(widget)

        self.switch_page("Dashboard", self.dashboard_btn)

    def create_top_header(self):
        header_widget = QWidget()
        header_widget.setObjectName("top-header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 10, 30, 10)
        header_layout.setSpacing(15)

        title_layout = QVBoxLayout()
        self.header_title = QLabel("Dashboard")
        self.header_title.setObjectName("header-title")
        self.header_subtitle = QLabel("Overview of your billing system")
        self.header_subtitle.setObjectName("header-subtitle")
        title_layout.addWidget(self.header_title)
        title_layout.addWidget(self.header_subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        import_btn = QPushButton("Import")
        import_btn.setObjectName("header-button")
        import_btn.clicked.connect(self.handle_import_csv)
        header_layout.addWidget(import_btn)

        export_btn = QPushButton("Export")
        export_btn.setObjectName("header-button")
        export_btn.clicked.connect(self.handle_export_csv)
        header_layout.addWidget(export_btn)
        
        quick_invoice_btn = QPushButton("+ Quick Invoice")
        quick_invoice_btn.setObjectName("primary-header-button")
        quick_invoice_btn.clicked.connect(lambda: self.switch_page("Create Invoice", self.create_invoice_btn))
        header_layout.addWidget(quick_invoice_btn)
        
        return header_widget

    def handle_import_csv(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("CSV Files (*.csv)")
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        if dialog.exec():
            file_name = dialog.selectedFiles()[0]
            if "companies" in file_name.lower() or "products" in file_name.lower():
                import_type = "companies_and_products"
            elif "invoice" in file_name.lower():
                import_type = "invoices"
            else:
                QMessageBox.critical(self, "Import Error", "Could not determine import type from file name.")
                return

            success, message = self.csv_manager.handle_import_csv(file_name, import_type)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Import Error", message)

    def handle_export_csv(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setNameFilter("CSV Files (*.csv)")
        dialog.setDefaultSuffix("csv")
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        if dialog.exec():
            file_name = dialog.selectedFiles()[0]
            if "companies" in file_name.lower() or "products" in file_name.lower():
                export_type = "companies_and_products"
            elif "invoice" in file_name.lower():
                export_type = "invoices"
            else:
                # Default to companies and products if not specified
                export_type = "companies_and_products"

            success, message = self.csv_manager.handle_export_csv(file_name, export_type)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Export Error", message)
            
    def create_nav_sidebar(self):
        nav_widget = QWidget()
        nav_widget.setObjectName("nav-sidebar")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(12, 20, 12, 20)
        nav_layout.setSpacing(10)

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(10, 0, 10, 20)
        title = QLabel("BillTracker Pro")
        title.setObjectName("sidebar-title")
        subtitle = QLabel("Indian Billing System")
        subtitle.setObjectName("sidebar-subtitle")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        nav_layout.addLayout(title_layout)

        self.dashboard_btn = self.create_nav_button("Dashboard", "dashboard.svg")
        self.companies_products_btn = self.create_nav_button("Companies & Products", "company.svg")
        self.create_invoice_btn = self.create_nav_button("Create Invoice", "create.svg")
        self.history_btn = self.create_nav_button("Past Invoices", "history.svg")
        self.inventory_btn = self.create_nav_button("Inventory", "inventory.svg")
        self.audit_log_btn = self.create_nav_button("Audit Log", "history.svg") # Using history icon for now
        self.settings_btn = self.create_nav_button("Settings", "settings.svg")
        
        nav_buttons = [self.dashboard_btn, self.companies_products_btn, self.create_invoice_btn, self.history_btn, self.inventory_btn, self.audit_log_btn]
        for btn in nav_buttons:
            btn.clicked.connect(lambda checked, b=btn: self.switch_page(b.text(), b))
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        self.settings_btn.clicked.connect(lambda checked, b=self.settings_btn: self.switch_page(b.text(), b))
        nav_layout.addWidget(self.settings_btn)

        return nav_widget

    def create_nav_button(self, text, icon_name):
        button = QPushButton(text)
        icon_path = os.path.join(self.resource_path, 'icons', icon_name)
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
        button.setCheckable(True)
        return button

    def switch_page(self, name, button):
        if self.active_nav_button:
            self.active_nav_button.setChecked(False)
        button.setChecked(True)
        self.active_nav_button = button
        
        self.stacked_widget.setCurrentWidget(self.tabs_map[name])
        self.header_title.setText(name)
        self.header_subtitle.setText(f"Manage your {name.lower()}")

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {DARK_THEME['bg_main']}; font-family: Roboto; }}
            #nav-sidebar {{ background-color: {DARK_THEME['bg_sidebar']}; border:none; }}
            #sidebar-title {{ font-size: 18px; font-weight: 600; color: {DARK_THEME['text_primary']}; }}
            #sidebar-subtitle {{ font-size: 12px; color: {DARK_THEME['text_secondary']}; }}
            
            #nav-sidebar QPushButton {{
                color: {DARK_THEME['text_secondary']}; border: none; text-align: left;
                padding: 10px 15px; border-radius: 6px; font-weight: 500; font-size: 14px;
            }}
            #nav-sidebar QPushButton:hover {{ background-color: {DARK_THEME['bg_hover']}; }}
            #nav-sidebar QPushButton:checked {{
                background-color: {DARK_THEME['bg_surface']};
                color: {DARK_THEME['accent_primary']};
                font-weight: 600;
            }}
            
            #top-header {{ background-color: {DARK_THEME['bg_surface']}; border-bottom: 1px solid {DARK_THEME['border_main']}; }}
            #header-title {{ font-size: 20px; font-weight: 600; color: {DARK_THEME['text_primary']}; }}
            #header-subtitle {{ font-size: 13px; color: {DARK_THEME['text_secondary']}; }}
            
            #header-button {{
                background-color: transparent; color: {DARK_THEME['text_secondary']};
                border: 1px solid {DARK_THEME['border_main']};
                padding: 8px 16px; border-radius: 6px; font-weight: 500;
            }}
            #header-button:hover {{ border-color: {DARK_THEME['accent_primary']}; color: {DARK_THEME['accent_primary']}; }}
            
            #primary-header-button {{
                background-color: {DARK_THEME['accent_primary']}; color: {DARK_THEME['text_on_accent']};
                border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600;
            }}
            #primary-header-button:hover {{ background-color: {DARK_THEME['accent_hover']}; }}
        """)
