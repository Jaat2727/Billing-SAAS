# src/tabs/dashboard_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from src.utils.theme import DARK_THEME
from src.utils.database import SessionLocal
from src.models import Invoice, CustomerCompany, Product

class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db_session = SessionLocal()
        self.init_ui()
        self.load_dashboard_data()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Stats Cards
        stats_layout = QHBoxLayout()
        self.total_invoices_card = self.create_stat_card("Total Invoices", "0")
        self.total_companies_card = self.create_stat_card("Total Customers", "0")
        self.total_revenue_card = self.create_stat_card("Total Revenue", "₹0.00")
        stats_layout.addWidget(self.total_invoices_card)
        stats_layout.addWidget(self.total_companies_card)
        stats_layout.addWidget(self.total_revenue_card)
        main_layout.addLayout(stats_layout)

        # Graphs and other info
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # Placeholder for graphs
        invoice_trends_graph = self.create_graph_placeholder("Invoice Trends (Coming Soon)")
        top_products_graph = self.create_graph_placeholder("Top Products (Coming Soon)")

        grid_layout.addWidget(invoice_trends_graph, 0, 0)
        grid_layout.addWidget(top_products_graph, 0, 1)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

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

    def create_graph_placeholder(self, title):
        graph_frame = QFrame()
        graph_frame.setObjectName("graph-card")
        layout = QVBoxLayout(graph_frame)
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return graph_frame

    def load_dashboard_data(self):
        total_invoices = self.db_session.query(Invoice).count()
        total_companies = self.db_session.query(CustomerCompany).count()
        total_revenue = sum(inv.total_amount for inv in self.db_session.query(Invoice).all())

        self.total_invoices_card.findChild(QLabel, "stat-value").setText(str(total_invoices))
        self.total_companies_card.findChild(QLabel, "stat-value").setText(str(total_companies))
        self.total_revenue_card.findChild(QLabel, "stat-value").setText(f"₹{total_revenue:,.2f}")

    def apply_styles(self):
        self.setStyleSheet(f"""
            QFrame#stat-card {{
                background-color: {DARK_THEME['bg_surface']};
                border: 1px solid {DARK_THEME['border_main']};
                border-radius: 8px;
                padding: 15px;
            }}
            QLabel#stat-title {{
                color: {DARK_THEME['text_secondary']};
                font-size: 14px;
                font-weight: 500;
            }}
            QLabel#stat-value {{
                color: {DARK_THEME['text_primary']};
                font-size: 28px;
                font-weight: 600;
                padding-top: 5px;
            }}
            QFrame#graph-card {{
                background-color: {DARK_THEME['bg_surface']};
                border: 1px solid {DARK_THEME['border_main']};
                border-radius: 8px;
                padding: 20px;
                min-height: 200px;
            }}
            QFrame#graph-card QLabel {{
                color: {DARK_THEME['text_secondary']};
                font-size: 16px;
            }}
        """)
