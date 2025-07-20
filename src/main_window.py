import os
import csv
import re
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.utils.theme import DARK_THEME
from src.utils.database import SessionLocal
from src.models import CustomerCompany, Product, Inventory
from src.utils.helpers import log_action
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
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Companies & Products", "", "CSV Files (*.csv)")
        if not file_name: return

        try:
            with SessionLocal() as db_session:
                companies_cache = {c.name: c for c in db_session.query(CustomerCompany).all()}
                
                with open(file_name, mode='r', encoding='utf-8-sig') as infile:
                    reader = csv.DictReader(infile)
                    for row in reader:
                        company_name = row.get('CompanyName', '').strip()
                        if not company_name: continue
                        
                        company = companies_cache.get(company_name)
                        if not company:
                            state_raw = row.get('State', '').strip()
                            state_name, state_code = self.parse_state(state_raw)
                            
                            company = CustomerCompany(
                                name=company_name, address=row.get('Address', '').strip(),
                                state=state_name, state_code=state_code,
                                gstin=row.get('GSTIN', '').strip()
                            )
                            db_session.add(company)
                            db_session.flush()
                            companies_cache[company_name] = company

                        product_name = row.get('ProductName', '').strip()
                        if product_name:
                            price_str = row.get('Price', '0').strip()
                            price = float(price_str) if price_str else 0.0
                            new_product = Product(name=product_name, price=price, company_id=company.id)
                            new_inventory = Inventory(stock_quantity=0, product=new_product)
                            db_session.add(new_product)
                            db_session.add(new_inventory)

                log_action(db_session, "IMPORT", "System", None, f"Imported data from CSV file: {os.path.basename(file_name)}.")
                db_session.commit()
            
            self.companies_tab_instance.load_companies()
            self.inventory_tab_instance.load_inventory_data()
            self.audit_log_tab_instance.load_logs()
            QMessageBox.information(self, "Success", "Data imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"An error occurred during import:\n{e}")

    def parse_state(self, state_raw):
        match = re.search(r"(.+?)\s*\(Code:\s*(\d+)\)", state_raw)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return state_raw, ""

    def handle_export_csv(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Companies & Products", "companies_products_backup.csv", "CSV Files (*.csv)")
        if not file_name: return

        try:
            with SessionLocal() as db_session:
                companies = db_session.query(CustomerCompany).order_by(CustomerCompany.name).all()
                with open(file_name, mode='w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerow(['CompanyName', 'CompanyID', 'Address', 'State', 'GSTIN', 'ProductID', 'ProductName', 'Price'])
                    
                    for company in companies:
                        state_formatted = f"{company.state} (Code: {company.state_code})"
                        if not company.products:
                            writer.writerow([company.name, company.id, company.address, state_formatted, company.gstin, '', '', ''])
                        else:
                            for product in sorted(company.products, key=lambda p: p.name):
                                writer.writerow([company.name, company.id, company.address, state_formatted, company.gstin, product.id, product.name, product.price])
                
                log_action(db_session, "EXPORT", "System", None, f"Exported data to CSV file: {os.path.basename(file_name)}.")
                db_session.commit()
            
            self.audit_log_tab_instance.load_logs()
            QMessageBox.information(self, "Success", "Data exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during export:\n{e}")
            
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
