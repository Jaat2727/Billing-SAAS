# src/tabs/dashboard_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from sqlalchemy import func
from src.utils.theme import DARK_THEME
from src.utils.database import SessionLocal
from src.models import Invoice, CustomerCompany, InvoiceItem

from src.tabs.base_tab import BaseTab

class DashboardTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.db_session = self.get_db_session()
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

from src.utils.plot_canvas import PlotCanvas

        # Graphs and other info
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        self.top_products_chart = PlotCanvas(self, width=5, height=4)
        self.invoice_stats_chart = PlotCanvas(self, width=5, height=4)

        grid_layout.addWidget(self.top_products_chart, 0, 0)
        grid_layout.addWidget(self.invoice_stats_chart, 0, 1)

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
        paid_invoices = self.db_session.query(Invoice).filter(Invoice.payment_status == "Paid").count()
        unpaid_invoices = total_invoices - paid_invoices
        total_companies = self.db_session.query(CustomerCompany).count()
        total_revenue = self.db_session.query(func.sum(Invoice.total_amount)).scalar() or 0

        top_products = self.db_session.query(
            InvoiceItem.product_name,
            func.sum(InvoiceItem.quantity)
        ).group_by(InvoiceItem.product_name).order_by(func.sum(InvoiceItem.quantity).desc()).limit(5).all()

        top_companies = self.db_session.query(
            CustomerCompany.name,
            func.sum(Invoice.total_amount)
        ).join(Invoice.customer).group_by(CustomerCompany.name).order_by(func.sum(Invoice.total_amount).desc()).limit(5).all()


        self.total_invoices_card.findChild(QLabel, "stat-value").setText(str(total_invoices))
        self.total_companies_card.findChild(QLabel, "stat-value").setText(str(total_companies))
        self.total_revenue_card.findChild(QLabel, "stat-value").setText(f"₹{total_revenue:,.2f}")

        # Update graphs
        self.top_products_chart.plot_bar(
            [p[0] for p in top_products],
            [p[1] for p in top_products],
            "Top 5 Products by Quantity Sold",
            "Product",
            "Quantity Sold"
        )
        self.invoice_stats_chart.plot_pie(
            [paid_invoices, unpaid_invoices],
            ["Paid", "Unpaid"],
            "Invoice Status"
        )

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
