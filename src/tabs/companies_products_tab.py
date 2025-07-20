from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
                             QPushButton, QFrame, QStackedWidget, QTableWidget, QTableWidgetItem, QAbstractItemView,
                             QHeaderView, QMenu, QMessageBox, QCheckBox, QLineEdit)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from src.utils.theme import APP_THEME
from src.utils.database import SessionLocal
from src.models import CustomerCompany, Product, Inventory
from src.utils.dialogs import CompanyDialog, ProductDialog
from src.utils.helpers import log_action

class SelectableListItemWidget(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        self.checkbox = QCheckBox()
        self.label = QLabel(text)
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setObjectName("menu-button")
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.menu_btn)

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

        left_panel = QFrame()
        left_panel.setObjectName("left-panel")
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400)
        left_layout.setContentsMargins(0,0,0,0)

        company_header = QFrame()
        company_header.setObjectName("panel-header")
        company_header_layout = QHBoxLayout(company_header)
        company_header_layout.addWidget(QLabel("Registered Companies"))
        company_header_layout.addStretch()
        self.delete_selected_companies_btn = QPushButton("Delete Selected")
        self.delete_selected_companies_btn.setObjectName("destructive-button")
        self.delete_selected_companies_btn.setEnabled(False)
        self.delete_selected_companies_btn.clicked.connect(self.handle_bulk_delete_companies)
        company_header_layout.addWidget(self.delete_selected_companies_btn)
        add_company_btn = QPushButton("+")
        add_company_btn.setObjectName("add-button")
        add_company_btn.clicked.connect(self.show_add_company_dialog)
        company_header_layout.addWidget(add_company_btn)

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

        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0)
        self.product_stack = QStackedWidget()

        placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label = QLabel("Select a company to manage its details and products.")
        placeholder_label.setObjectName("placeholder-label")
        placeholder_layout.addWidget(placeholder_label)

        product_view_widget = QWidget()
        product_view_layout = QVBoxLayout(product_view_widget)
        product_header = QFrame()
        product_header.setObjectName("panel-header")
        product_header_layout = QHBoxLayout(product_header)
        self.company_detail_title = QLabel("Products")
        self.delete_selected_products_btn = QPushButton("Delete Selected")
        self.delete_selected_products_btn.setObjectName("destructive-button")
        self.delete_selected_products_btn.setEnabled(False)
        self.delete_selected_products_btn.clicked.connect(self.handle_bulk_delete_products)
        self.add_product_btn = QPushButton("+ Add Product")
        self.add_product_btn.setObjectName("primary-button")
        self.add_product_btn.setEnabled(False)
        self.add_product_btn.clicked.connect(self.show_add_product_dialog)
        product_header_layout.addWidget(self.company_detail_title)
        product_header_layout.addStretch()
        product_header_layout.addWidget(self.delete_selected_products_btn)
        product_header_layout.addWidget(self.add_product_btn)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(["", "Product Name", "Price", ""])
        self.product_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        product_view_layout.addWidget(product_header)
        product_view_layout.addWidget(self.product_table, 1)

        self.product_stack.addWidget(placeholder_widget)
        self.product_stack.addWidget(product_view_widget)
        right_layout.addWidget(self.product_stack)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

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
            item_widget = SelectableListItemWidget(company.name)
            item_widget.checkbox.stateChanged.connect(self.update_delete_button_state)
            menu = QMenu(self)
            edit_action = QAction("Edit Details", menu)
            edit_action.triggered.connect(lambda chk, c=company: self.show_edit_company_dialog(c))
            delete_action = QAction("Delete Company", menu)
            delete_action.triggered.connect(lambda chk, c=company: self.handle_delete_company(c))
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            item_widget.menu_btn.setMenu(menu)
            list_item = QListWidgetItem(self.company_list)
            list_item.setSizeHint(item_widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, company.id)
            self.company_list.addItem(list_item)
            self.company_list.setItemWidget(list_item, item_widget)
            if company.id == current_id: self.company_list.setCurrentItem(list_item)
        self.update_delete_button_state()
        self.on_company_selection_changed()

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
            self.add_product_btn.setEnabled(True)
        self.update_delete_button_state()

    def load_products_for_company(self):
        self.product_table.setRowCount(0)
        if not self.selected_company: return
        for product in sorted(self.selected_company.products, key=lambda p:p.name):
            row_pos = self.product_table.rowCount()
            self.product_table.insertRow(row_pos)
            checkbox_widget = QWidget(); checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox = QCheckBox(); checkbox.stateChanged.connect(self.update_delete_button_state)
            checkbox_layout.addWidget(checkbox); checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_widget.setProperty("product_id", product.id)
            self.product_table.setCellWidget(row_pos, 0, checkbox_widget)
            self.product_table.setItem(row_pos, 1, QTableWidgetItem(product.name))
            self.product_table.setItem(row_pos, 2, QTableWidgetItem(f"₹{product.price:,.2f}"))
            actions_btn = QPushButton("⋮"); actions_btn.setObjectName("menu-button")
            menu = QMenu(self)
            edit_action = QAction("Edit", menu); edit_action.triggered.connect(lambda chk, p=product: self.show_edit_product_dialog(p))
            delete_action = QAction("Delete", menu); delete_action.triggered.connect(lambda chk, p=product: self.handle_delete_product(p))
            menu.addAction(edit_action); menu.addAction(delete_action)
            actions_btn.setMenu(menu); self.product_table.setCellWidget(row_pos, 3, actions_btn)
        self.update_delete_button_state()

    def get_checked_company_ids(self):
        checked_ids = []
        for i in range(self.company_list.count()):
            item = self.company_list.item(i); widget = self.company_list.itemWidget(item)
            checkbox = widget.findChild(QCheckBox);
            if checkbox and checkbox.isChecked(): checked_ids.append(item.data(Qt.ItemDataRole.UserRole))
        return checked_ids

    def get_checked_product_ids(self):
        checked_ids = []
        for i in range(self.product_table.rowCount()):
            widget = self.product_table.cellWidget(i, 0); checkbox = widget.findChild(QCheckBox)
            if checkbox and checkbox.isChecked(): checked_ids.append(widget.property("product_id"))
        return checked_ids

    def update_delete_button_state(self):
        self.delete_selected_companies_btn.setEnabled(len(self.get_checked_company_ids()) > 0)
        self.delete_selected_products_btn.setEnabled(len(self.get_checked_product_ids()) > 0)

    def show_add_company_dialog(self):
        dialog = CompanyDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name']:
                new_company = CustomerCompany(**data)
                self.db_session.add(new_company); self.db_session.flush()
                log_action(self.db_session, "CREATE", "Company", new_company.id, f"Company '{new_company.name}' created.")
                self.db_session.commit(); self.load_companies()

    def show_edit_company_dialog(self, company):
        dialog = CompanyDialog(company=company, parent=self)
        if dialog.exec():
            data = dialog.get_data(); details = f"Updated company '{company.name}'."
            for key, value in data.items(): setattr(company, key, value)
            log_action(self.db_session, "UPDATE", "Company", company.id, details)
            self.db_session.commit(); self.load_companies()

    def handle_delete_company(self, company):
        product_count = len(company.products)
        title = "Confirm Deletion"; text = f"Are you sure you want to delete '{company.name}'? This action cannot be undone."
        if product_count > 0: text = f"Are you sure you want to delete '{company.name}'?\n\nThis will also permanently delete its {product_count} associated products. This action cannot be undone."
        reply = QMessageBox.question(self, title, text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            details = f"Company '{company.name}' and its {product_count} products deleted."
            log_action(self.db_session, "DELETE", "Company", company.id, details)
            self.db_session.delete(company); self.db_session.commit()
            self.load_companies(); self.product_stack.setCurrentIndex(0)

    def handle_bulk_delete_companies(self):
        company_ids_to_delete = self.get_checked_company_ids()
        if not company_ids_to_delete: return
        product_count = sum(len(self.db_session.get(CustomerCompany, cid).products) for cid in company_ids_to_delete)
        title = "Confirm Bulk Deletion"; text = f"Are you sure you want to delete these {len(company_ids_to_delete)} companies?"
        if product_count > 0: text += f"\n\nThis will also permanently delete a total of {product_count} associated products. This action cannot be undone."
        reply = QMessageBox.question(self, title, text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for cid in company_ids_to_delete:
                company = self.db_session.get(CustomerCompany, cid)
                details = f"Company '{company.name}' and its products deleted in bulk."
                log_action(self.db_session, "DELETE", "Company", cid, details)
                self.db_session.delete(company)
            self.db_session.commit(); self.load_companies()
            if self.selected_company and self.selected_company.id in company_ids_to_delete: self.product_stack.setCurrentIndex(0)

    def show_add_product_dialog(self):
        if not self.selected_company: return
        dialog = ProductDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name']:
                new_product = Product(name=data['name'], price=data['price'], company_id=self.selected_company.id)
                new_inventory = Inventory(stock_quantity=0, product=new_product)
                self.db_session.add(new_product); self.db_session.add(new_inventory); self.db_session.flush()
                log_action(self.db_session, "CREATE", "Product", new_product.id, f"Product '{new_product.name}' created for company '{self.selected_company.name}'.")
                self.db_session.commit(); self.load_products_for_company()

    def show_edit_product_dialog(self, product):
        dialog = ProductDialog(product=product, parent=self)
        if dialog.exec():
            data = dialog.get_data(); product.name = data['name']; product.price = data['price']
            log_action(self.db_session, "UPDATE", "Product", product.id, f"Product '{product.name}' updated.")
            self.db_session.commit(); self.load_products_for_company()

    def handle_delete_product(self, product):
        reply = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete '{product.name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            log_action(self.db_session, "DELETE", "Product", product.id, f"Product '{product.name}' deleted.")
            self.db_session.delete(product); self.db_session.commit(); self.load_products_for_company()

    def handle_bulk_delete_products(self):
        product_ids_to_delete = self.get_checked_product_ids()
        if not product_ids_to_delete: return
        reply = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete these {len(product_ids_to_delete)} products?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for pid in product_ids_to_delete:
                product = self.db_session.get(Product, pid)
                log_action(self.db_session, "DELETE", "Product", pid, f"Product '{product.name}' deleted in bulk.")
                self.db_session.delete(product)
            self.db_session.commit(); self.load_products_for_company()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{ font-family: Roboto; }}
            QFrame#left-panel {{ background-color: {APP_THEME['bg_content']}; }}
            QFrame#panel-header {{
                border-bottom: 1px solid {APP_THEME['border']};
                padding: 10px 15px;
            }}
            QFrame#search-frame {{ padding: 10px; }}
            #panel-header QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {APP_THEME['text_primary']};
            }}
            #placeholder-label {{
                color: {APP_THEME['text_secondary']};
                font-size: 16px;
            }}
            QListWidget {{ border: none; }}
            SelectableListItemWidget {{
                border-radius: 6px;
                margin: 2px 10px;
                border: 1px solid transparent;
            }}
            SelectableListItemWidget QLabel {{ color: {APP_THEME['text_primary']}; font-size: 14px; }}
            SelectableListItemWidget[selected=true] {{
                background-color: {APP_THEME['accent_blue_light_bg']};
                border-left: 3px solid {APP_THEME['accent_blue']};
            }}
            SelectableListItemWidget[selected=true] QLabel {{
                color: {APP_THEME['accent_blue']};
                font-weight: 600;
            }}
            #add-button, #menu-button {{
                background-color: transparent;
                color: {APP_THEME['text_secondary']};
                border: none;
                font-size: 18px;
                font-weight: bold;
                max-width: 30px;
                border-radius: 6px;
            }}
            #add-button:hover, #menu-button:hover {{
                color: {APP_THEME['accent_blue']};
            }}
            #primary-button {{
                background-color: {APP_THEME['accent_blue']};
                color: {APP_THEME['text_white']};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }}
            #primary-button:hover {{
                background-color: {APP_THEME['accent_blue_hover']};
            }}
            #primary-button:disabled {{
                background-color: {APP_THEME['bg_main']};
                color: {APP_THEME['text_secondary']};
            }}
            #destructive-button {{
                background-color: transparent;
                color: {APP_THEME['danger']};
                border: 1px solid {APP_THEME['danger']};
                padding: 5px 10px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }}
            #destructive-button:hover {{
                background-color: {APP_THEME['danger_hover']};
                color: {APP_THEME['text_white']};
                border-color: {APP_THEME['danger_hover']};
            }}
            #destructive-button:disabled {{
                color: {APP_THEME['text_secondary']};
                border-color: {APP_THEME['border']};
                background-color: transparent;
            }}
            QTableWidget {{
                background-color: transparent;
                gridline-color: {APP_THEME['border']};
                border: none;
            }}
            QHeaderView::section {{
                background-color: {APP_THEME['bg_main']};
                color: {APP_THEME['text_secondary']};
                padding: 10px;
                border: none;
                font-weight: 600;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {APP_THEME['border']};
                color: {APP_THEME['text_secondary']};
                font-size: 14px;
            }}
            QTableWidget::item:selected {{
                background-color: {APP_THEME['accent_blue_light_bg']};
                color: {APP_THEME['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {APP_THEME['border']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {APP_THEME['accent_blue']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {APP_THEME['accent_blue']};
                border-color: {APP_THEME['accent_blue']};
                image: url(resources/icons/check.svg);
            }}
        """)
