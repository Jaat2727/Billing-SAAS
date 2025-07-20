# src/tabs/audit_log_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QHBoxLayout, QLabel, QAbstractItemView)
from PyQt6.QtCore import Qt
from src.utils.database import SessionLocal
from src.models import AuditLog
from src.utils.theme import APP_THEME

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

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Action", "Entity", "Details"])
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.log_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

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
                background-color: {APP_THEME['bg_content']};
                gridline-color: {APP_THEME['border']};
                border: 1px solid {APP_THEME['border']};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background-color: {APP_THEME['bg_main']};
                color: {APP_THEME['text_secondary']};
                padding: 12px;
                border: none;
                border-bottom: 1px solid {APP_THEME['border']};
                font-weight: 600;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {APP_THEME['border']};
                color: {APP_THEME['text_secondary']};
            }}
        """)
