from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
                             QPushButton, QFrame, QStackedWidget, QTableWidget, QTableWidgetItem, QAbstractItemView,
                             QHeaderView, QMenu, QMessageBox, QCheckBox, QLineEdit)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize
from src.utils.theme import DARK_THEME
from src.utils.database import SessionLocal
from src.models import CustomerCompany, Product, Inventory
from src.utils.dialogs import CompanyDialog, ProductDialog
from src.utils.helpers import log_action

class CompaniesProductsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db_session = SessionLocal()
        self.selected_company = None
        self.init_ui()
        self.load_companies()
        self.apply_styles()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(1)

        # Left Panel for Companies
        left_panel = QFrame()
        left_panel.setObjectName("left-panel")
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400)
        left_layout.setContentsMargins(0,0,0,0)

        company_header = self.create_panel_header("Registered Companies", self.show_add_company_dialog, self.handle_bulk_delete_companies)
        left_layout.addWidget(company_header)

        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_frame.setObjectName("search-frame")
        self.company_search_input = QLineEdit()
        self.company_search_input.setPlaceholderText("Search companies...")
        self.company_search_input.textChanged.connect(self.filter_companies)
        search_layout.addWidget(self.company_search_input)
        left_layout.addWidget(search_frame)

        self.company_list = QListWidget()
        self.company_list.itemSelectionChanged.connect(self.on_company_selection_changed)
        self.company_list.itemClicked.connect(self.on_company_selected)
        left_layout.addWidget(self.company_list)

        # Right Panel for Products
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0)
        self.product_stack = QStackedWidget()

        # Placeholder
        placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label = QLabel("Select a company to manage its details and products.")
        placeholder_label.setObjectName("placeholder-label")
        placeholder_layout.addWidget(placeholder_label)

        # Product View
        product_view_widget = QWidget()
        product_view_layout = QVBoxLayout(product_view_widget)
        self.product_header = self.create_panel_header("Products", self.show_add_product_dialog, self.handle_bulk_delete_products)
        self.company_detail_title = self.product_header.findChild(QLabel)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(["", "Product Name", "Price", ""])
        self.product_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        product_view_layout.addWidget(self.product_header)
        product_view_layout.addWidget(self.product_table, 1)

        self.product_stack.addWidget(placeholder_widget)
        self.product_stack.addWidget(product_view_widget)
        right_layout.addWidget(self.product_stack)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

    def create_panel_header(self, title_text, add_callback, delete_callback):
        header = QFrame()
        header.setObjectName("panel-header")
        layout = QHBoxLayout(header)
        title = QLabel(title_text)
        layout.addWidget(title)
        layout.addStretch()

        delete_btn = QPushButton("Delete Selected")
        delete_btn.setObjectName("destructive-button")
        delete_btn.setEnabled(False)
        delete_btn.clicked.connect(delete_callback)
        layout.addWidget(delete_btn)

        add_btn = QPushButton("+")
        add_btn.setObjectName("add-button")
        add_btn.clicked.connect(add_callback)
        layout.addWidget(add_btn)

        header.setProperty("delete_button", delete_btn)
        return header

    def filter_companies(self):
        search_text = self.company_search_input.text().lower()
        for i in range(self.company_list.count()):
            item = self.company_list.item(i)
            widget = self.company_list.itemWidget(item)
            item.setHidden(search_text not in widget.label.text().lower())

    def load_companies(self):
        current_selection = self.company_list.currentItem()
        current_id = current_selection.data(Qt.ItemDataRole.UserRole) if current_selection else None
        self.company_list.clear()
        companies = self.db_session.query(CustomerCompany).order_by(CustomerCompany.name).all()
        for company in companies:
            item_widget = self.create_list_item_widget(company.name, company)
            list_item = QListWidgetItem(self.company_list)
            list_item.setSizeHint(item_widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, company.id)
            self.company_list.addItem(list_item)
            self.company_list.setItemWidget(list_item, item_widget)
            if company.id == current_id: self.company_list.setCurrentItem(list_item)
        self.update_delete_button_state()

    def create_list_item_widget(self, text, entity):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.update_delete_button_state)

        label = QLabel(text)

        menu_btn = QPushButton("⋮")
        menu_btn.setObjectName("menu-button")

        menu = QMenu(self)
        edit_action = QAction("Edit", menu)
        delete_action = QAction("Delete", menu)

        if isinstance(entity, CustomerCompany):
            edit_action.triggered.connect(lambda chk, c=entity: self.show_edit_company_dialog(c))
            delete_action.triggered.connect(lambda chk, c=entity: self.handle_delete_company(c))
        elif isinstance(entity, Product):
            edit_action.triggered.connect(lambda chk, p=entity: self.show_edit_product_dialog(p))
            delete_action.triggered.connect(lambda chk, p=entity: self.handle_delete_product(p))

        menu.addAction(edit_action)
        menu.addAction(delete_action)
        menu_btn.setMenu(menu)

        layout.addWidget(checkbox)
        layout.addWidget(label, 1)
        layout.addWidget(menu_btn)

        widget.setProperty("checkbox", checkbox)
        return widget

    def on_company_selection_changed(self):
        for i in range(self.company_list.count()):
            item = self.company_list.item(i)
            widget = self.company_list.itemWidget(item)
            widget.setProperty("selected", item.isSelected())
            widget.style().polish(widget)

    def on_company_selected(self, item):
        company_id = item.data(Qt.ItemDataRole.UserRole)
        self.selected_company = self.db_session.query(CustomerCompany).get(company_id)
        if self.selected_company:
            self.company_detail_title.setText(f"Products for: {self.selected_company.name}")
            self.load_products_for_company()
            self.product_stack.setCurrentIndex(1)
            self.product_header.findChild(QPushButton, "add-button").setEnabled(True)
        self.update_delete_button_state()

    def load_products_for_company(self):
        self.product_table.setRowCount(0)
        if not self.selected_company: return
        for product in sorted(self.selected_company.products, key=lambda p:p.name):
            row_pos = self.product_table.rowCount()
            self.product_table.insertRow(row_pos)

            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.update_delete_button_state)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_widget.setProperty("product_id", product.id)
            checkbox_widget.setProperty("checkbox", checkbox)
            self.product_table.setCellWidget(row_pos, 0, checkbox_widget)

            self.product_table.setItem(row_pos, 1, QTableWidgetItem(product.name))
            self.product_table.setItem(row_pos, 2, QTableWidgetItem(f"₹{product.price:,.2f}"))

            actions_btn = QPushButton("⋮")
            actions_btn.setObjectName("menu-button")
            menu = QMenu(self)
            edit_action = QAction("Edit", menu)
            edit_action.triggered.connect(lambda chk, p=product: self.show_edit_product_dialog(p))
            delete_action = QAction("Delete", menu)
            delete_action.triggered.connect(lambda chk, p=product: self.handle_delete_product(p))
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            actions_btn.setMenu(menu)
            self.product_table.setCellWidget(row_pos, 3, actions_btn)
        self.update_delete_button_state()

    def get_checked_company_ids(self):
        checked_ids = []
        for i in range(self.company_list.count()):
            item = self.company_list.item(i)
            widget = self.company_list.itemWidget(item)
            checkbox = widget.property("checkbox")
            if checkbox and checkbox.isChecked():
                checked_ids.append(item.data(Qt.ItemDataRole.UserRole))
        return checked_ids

    def get_checked_product_ids(self):
        checked_ids = []
        for i in range(self.product_table.rowCount()):
            widget = self.product_table.cellWidget(i, 0)
            checkbox = widget.property("checkbox")
            if checkbox and checkbox.isChecked():
                checked_ids.append(widget.property("product_id"))
        return checked_ids

    def update_delete_button_state(self):
        # Company delete button
        company_delete_btn = self.company_header.property("delete_button")
        company_delete_btn.setEnabled(len(self.get_checked_company_ids()) > 0)

        # Product delete button
        product_delete_btn = self.product_header.property("delete_button")
        product_delete_btn.setEnabled(len(self.get_checked_product_ids()) > 0)

    def show_add_company_dialog(self):
        dialog = CompanyDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name']:
                new_company = CustomerCompany(**data)
                self.db_session.add(new_company)
                self.db_session.flush()
                log_action(self.db_session, "CREATE", "Company", new_company.id, f"Company '{new_company.name}' created.")
                self.db_session.commit()
                self.load_companies()

    def show_edit_company_dialog(self, company):
        dialog = CompanyDialog(company=company, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            details = f"Updated company '{company.name}'."
            for key, value in data.items():
                setattr(company, key, value)
            log_action(self.db_session, "UPDATE", "Company", company.id, details)
            self.db_session.commit()
            self.load_companies()

    def handle_delete_company(self, company):
        product_count = len(company.products)
        title = "Confirm Deletion"
        text = f"Are you sure you want to delete '{company.name}'? This action cannot be undone."
        if product_count > 0:
            text = f"Are you sure you want to delete '{company.name}'?\n\nThis will also permanently delete its {product_count} associated products. This action cannot be undone."

        reply = QMessageBox.question(self, title, text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            details = f"Company '{company.name}' and its {product_count} products deleted."
            log_action(self.db_session, "DELETE", "Company", company.id, details)
            self.db_session.delete(company)
            self.db_session.commit()
            self.load_companies()
            self.product_stack.setCurrentIndex(0)

    def handle_bulk_delete_companies(self):
        company_ids_to_delete = self.get_checked_company_ids()
        if not company_ids_to_delete: return

        product_count = sum(len(self.db_session.get(CustomerCompany, cid).products) for cid in company_ids_to_delete)
        title = "Confirm Bulk Deletion"
        text = f"Are you sure you want to delete these {len(company_ids_to_delete)} companies?"
        if product_count > 0:
            text += f"\n\nThis will also permanently delete a total of {product_count} associated products. This action cannot be undone."

        reply = QMessageBox.question(self, title, text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for cid in company_ids_to_delete:
                company = self.db_session.get(CustomerCompany, cid)
                details = f"Company '{company.name}' and its products deleted in bulk."
                log_action(self.db_session, "DELETE", "Company", cid, details)
                self.db_session.delete(company)
            self.db_session.commit()
            self.load_companies()
            if self.selected_company and self.selected_company.id in company_ids_to_delete:
                self.product_stack.setCurrentIndex(0)

    def show_add_product_dialog(self):
        if not self.selected_company: return
        dialog = ProductDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name']:
                new_product = Product(name=data['name'], price=data['price'], company_id=self.selected_company.id)
                new_inventory = Inventory(stock_quantity=0, product=new_product)
                self.db_session.add(new_product)
                self.db_session.add(new_inventory)
                self.db_session.flush()
                log_action(self.db_session, "CREATE", "Product", new_product.id, f"Product '{new_product.name}' created for company '{self.selected_company.name}'.")
                self.db_session.commit()
                self.load_products_for_company()

    def show_edit_product_dialog(self, product):
        dialog = ProductDialog(product=product, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            product.name = data['name']
            product.price = data['price']
            log_action(self.db_session, "UPDATE", "Product", product.id, f"Product '{product.name}' updated.")
            self.db_session.commit()
            self.load_products_for_company()

    def handle_delete_product(self, product):
        reply = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete '{product.name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            log_action(self.db_session, "DELETE", "Product", product.id, f"Product '{product.name}' deleted.")
            self.db_session.delete(product)
            self.db_session.commit()
            self.load_products_for_company()

    def handle_bulk_delete_products(self):
        product_ids_to_delete = self.get_checked_product_ids()
        if not product_ids_to_delete: return
        reply = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete these {len(product_ids_to_delete)} products?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for pid in product_ids_to_delete:
                product = self.db_session.get(Product, pid)
                log_action(self.db_session, "DELETE", "Product", pid, f"Product '{product.name}' deleted in bulk.")
                self.db_session.delete(product)
            self.db_session.commit()
            self.load_products_for_company()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{ font-family: Roboto; }}
            QFrame#left-panel, QFrame#right-panel {{ background-color: {DARK_THEME['bg_surface']}; }}
            QFrame#panel-header {{
                border-bottom: 1px solid {DARK_THEME['border_main']};
                padding: 10px 15px;
            }}
            #panel-header QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {DARK_THEME['text_primary']};
            }}
            QFrame#search-frame {{ padding: 10px; }}
            QLineEdit {{
                background-color: {DARK_THEME['bg_input']};
                color: {DARK_THEME['text_primary']};
                border: 1px solid {DARK_THEME['border_main']};
                border-radius: 6px;
                padding: 8px;
            }}
            QListWidget {{ border: none; }}
            QListWidget::item {{ border-bottom: 1px solid {DARK_THEME['border_main']}; }}
            QWidget[selected=true] {{ background-color: {DARK_THEME['bg_hover']}; }}

            #placeholder-label {{
                color: {DARK_THEME['text_secondary']};
                font-size: 16px;
            }}

            #add-button, #menu-button {{
                background-color: transparent;
                color: {DARK_THEME['text_secondary']};
                border: none;
                font-size: 20px;
                font-weight: bold;
                max-width: 30px;
                border-radius: 6px;
            }}
            #add-button:hover, #menu-button:hover {{ color: {DARK_THEME['accent_primary']}; }}

            #destructive-button {{
                background-color: transparent;
                color: {DARK_THEME['accent_danger']};
                border: 1px solid {DARK_THEME['accent_danger']};
                padding: 5px 10px;
                border-radius: 6px;
                font-weight: 600;
            }}
            #destructive-button:hover {{
                background-color: {DARK_THEME['accent_danger_hover']};
                color: {DARK_THEME['text_on_accent']};
                border-color: {DARK_THEME['accent_danger_hover']};
            }}
            #destructive-button:disabled {{
                color: {DARK_THEME['text_secondary']};
                border-color: {DARK_THEME['text_secondary']};
                background-color: transparent;
            }}

            QTableWidget {{
                background-color: transparent;
                gridline-color: {DARK_THEME['border_main']};
                border: none;
            }}
            QHeaderView::section {{
                background-color: {DARK_THEME['bg_sidebar']};
                color: {DARK_THEME['text_secondary']};
                padding: 10px;
                border: none;
                font-weight: 600;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {DARK_THEME['border_main']};
                color: {DARK_THEME['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {DARK_THEME['border_main']};
            }}
            QCheckBox::indicator:hover {{ border-color: {DARK_THEME['accent_primary']}; }}
            QCheckBox::indicator:checked {{
                background-color: {DARK_THEME['accent_primary']};
                border-color: {DARK_THEME['accent_primary']};
            }}
        """)
