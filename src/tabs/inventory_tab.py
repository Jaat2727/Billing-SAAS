# src/tabs/inventory_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
                             QHeaderView, QPushButton, QMessageBox, QFrame, QLabel, QAbstractItemView)
from PyQt6.QtCore import Qt
from src.utils.database import SessionLocal
from src.models import CustomerCompany, Product, Inventory, InventoryHistory
from src.utils.dialogs import StockAdjustmentDialog
from src.utils.theme import DARK_THEME
from src.utils.helpers import log_action

class InventoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db_session = SessionLocal()
        self.init_ui()
        self.load_inventory_data()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)
        self.total_products_card = self.create_stat_card("Total Products", "0")
        self.low_stock_card = self.create_stat_card("Low Stock Items", "0")
        self.out_of_stock_card = self.create_stat_card("Out of Stock", "0")
        stats_layout.addWidget(self.total_products_card)
        stats_layout.addWidget(self.low_stock_card)
        stats_layout.addWidget(self.out_of_stock_card)
        stats_layout.addStretch()
        
        controls_frame = QFrame()
        controls_frame.setObjectName("panel-header")
        controls_layout = QHBoxLayout(controls_frame)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search product or company...")
        self.search_input.textChanged.connect(self.load_inventory_data)
        self.stock_filter_combo = QComboBox()
        self.stock_filter_combo.addItems(["All Stock", "Low Stock", "Out of Stock"])
        self.stock_filter_combo.currentIndexChanged.connect(self.load_inventory_data)
        controls_layout.addWidget(QLabel("Search:"))
        controls_layout.addWidget(self.search_input, 1)
        controls_layout.addWidget(QLabel("Filter by:"))
        controls_layout.addWidget(self.stock_filter_combo)

        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels(["Product Name", "Company", "Current Stock", "Price", "Actions"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.inventory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.inventory_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        main_layout.addWidget(stats_frame)
        main_layout.addWidget(controls_frame)
        main_layout.addWidget(self.inventory_table, 1)

    def create_stat_card(self, title, value):
        card = QFrame()
        card.setObjectName("stat-card")
        layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setObjectName("stat-title")
        value_label = QLabel(value)
        value_label.setObjectName("stat-value")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card

    def load_inventory_data(self):
        search_text = self.search_input.text().lower()
        stock_filter = self.stock_filter_combo.currentText()
        
        query = self.db_session.query(Product).join(Product.company)
        
        if search_text:
            query = query.filter(Product.name.ilike(f"%{search_text}%") | CustomerCompany.name.ilike(f"%{search_text}%"))

        all_products_for_stats = self.db_session.query(Product).all()
        
        if stock_filter == "Low Stock":
            product_ids = [p.id for p in all_products_for_stats if p.inventory and p.inventory.stock_quantity <= p.inventory.low_stock_threshold and p.inventory.stock_quantity > 0]
            query = query.filter(Product.id.in_(product_ids))
        elif stock_filter == "Out of Stock":
            product_ids = [p.id for p in all_products_for_stats if p.inventory and p.inventory.stock_quantity == 0]
            query = query.filter(Product.id.in_(product_ids))

        products = query.order_by(Product.name).all()
        
        self.inventory_table.setRowCount(0)
        low_stock_count = 0
        out_of_stock_count = 0
        
        for p in all_products_for_stats:
            stock = p.inventory.stock_quantity if p.inventory else 0
            low_thresh = p.inventory.low_stock_threshold if p.inventory else 10
            if stock <= low_thresh and stock > 0: low_stock_count += 1
            if stock == 0: out_of_stock_count += 1
            
        self.total_products_card.findChild(QLabel, "stat-value").setText(str(len(all_products_for_stats)))
        self.low_stock_card.findChild(QLabel, "stat-value").setText(str(low_stock_count))
        self.out_of_stock_card.findChild(QLabel, "stat-value").setText(str(out_of_stock_count))

        for product in products:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            self.inventory_table.setItem(row, 0, QTableWidgetItem(product.name))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(product.company.name))
            stock_value = product.inventory.stock_quantity if product.inventory else 0
            stock_item = QTableWidgetItem(str(stock_value))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inventory_table.setItem(row, 2, stock_item)
            price_item = QTableWidgetItem(f"₹{product.price:,.2f}")
            self.inventory_table.setItem(row, 3, price_item)
            adjust_btn = QPushButton("Adjust Stock")
            adjust_btn.setObjectName("secondary-button")
            adjust_btn.clicked.connect(lambda chk, p=product: self.show_adjust_stock_dialog(p))
            self.inventory_table.setCellWidget(row, 4, adjust_btn)

    def show_adjust_stock_dialog(self, product):
        current_stock = product.inventory.stock_quantity if product.inventory else 0
        dialog = StockAdjustmentDialog(product.name, current_stock, self)
        if dialog.exec():
            data = dialog.get_data()
            adjustment = data['adjustment']
            if adjustment != 0:
                if not product.inventory:
                    product.inventory = Inventory(stock_quantity=0, product=product)
                    self.db_session.add(product.inventory)

                details = f"Stock for '{product.name}' changed by {adjustment}. Old: {product.inventory.stock_quantity}, New: {product.inventory.stock_quantity + adjustment}."
                product.inventory.stock_quantity += adjustment

                history_entry = InventoryHistory(
                    product_id=product.id,
                    change_quantity=adjustment,
                    reason=data['reason'],
                    new_quantity=product.inventory.stock_quantity
                )
                self.db_session.add(history_entry)

                log_action(self.db_session, "STOCK_ADJUST", "Inventory", product.id, details)
                self.db_session.commit()
                self.load_inventory_data()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QFrame#stat-card {{ background-color: {DARK_THEME['bg_surface']}; border: 1px solid {DARK_THEME['border_main']}; border-radius: 8px; padding: 15px; }}
            QLabel#stat-title {{ color: {DARK_THEME['text_secondary']}; font-size: 13px; font-weight: 500; }}
            QLabel#stat-value {{ color: {DARK_THEME['text_primary']}; font-size: 24px; font-weight: 600; }}
            QFrame#panel-header {{ border-bottom: 1px solid {DARK_THEME['border_main']}; padding: 10px; }}
            QTableWidget {{ background-color: transparent; gridline-color: {DARK_THEME['border_main']}; border: none; }}
            QHeaderView::section {{ background-color: {DARK_THEME['bg_sidebar']}; color: {DARK_THEME['text_secondary']}; padding: 10px; border: none; font-weight: 600; }}
            QTableWidget::item {{ padding: 10px; border-bottom: 1px solid {DARK_THEME['border_main']}; color: {DARK_THEME['text_primary']}; }}
            QPushButton#secondary-button {{ background-color: transparent; color: {DARK_THEME['text_secondary']}; border: 1px solid {DARK_THEME['border_main']}; padding: 5px 10px; border-radius: 6px; }}
            QPushButton#secondary-button:hover {{ border-color: {DARK_THEME['accent_primary']}; color: {DARK_THEME['accent_primary']}; }}
        """)