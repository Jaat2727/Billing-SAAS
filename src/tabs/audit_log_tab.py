# src/tabs/audit_log_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QHBoxLayout, QLabel, QAbstractItemView, QPushButton)
from PyQt6.QtCore import Qt
from src.utils.database import SessionLocal
from src.models import AuditLog
from src.utils.theme import DARK_THEME

class AuditLogTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db_session = SessionLocal()
        self.init_ui()
        self.load_logs()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Application Action History"))
        header_layout.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("secondary-button")
        refresh_btn.clicked.connect(self.load_logs)
        header_layout.addWidget(refresh_btn)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Action", "Entity", "Details"])
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.log_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.log_table, 1)

    def load_logs(self):
        self.log_table.setRowCount(0)
        logs = self.db_session.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
        for log in logs:
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)
            self.log_table.setItem(row, 0, QTableWidgetItem(log.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
            self.log_table.setItem(row, 1, QTableWidgetItem(log.action))
            entity_str = f"{log.entity_type} (ID: {log.entity_id})" if log.entity_id else log.entity_type
            self.log_table.setItem(row, 2, QTableWidgetItem(entity_str))
            self.log_table.setItem(row, 3, QTableWidgetItem(log.details))

    def apply_styles(self):
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {DARK_THEME['bg_surface']};
                gridline-color: {DARK_THEME['border_main']};
                border: 1px solid {DARK_THEME['border_main']};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background-color: {DARK_THEME['bg_sidebar']};
                color: {DARK_THEME['text_secondary']};
                padding: 10px;
                border: none;
                border-bottom: 1px solid {DARK_THEME['border_main']};
                font-weight: 600;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {DARK_THEME['border_main']};
                color: {DARK_THEME['text_primary']};
            }}
            QPushButton#secondary-button {{
                background-color: transparent;
                color: {DARK_THEME['text_secondary']};
                border: 1px solid {DARK_THEME['border_main']};
                padding: 5px 10px;
                border-radius: 6px;
            }}
            QPushButton#secondary-button:hover {{
                border-color: {DARK_THEME['accent_primary']};
                color: {DARK_THEME['accent_primary']};
            }}
        """)
