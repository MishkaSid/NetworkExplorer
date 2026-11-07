
DARK_THEME = """
QMainWindow, QWidget {
    background-color: #0f172a;
    color: #f1f5f9;
    font-family: "Segoe UI";
    font-size: 13px;
}

QLabel {
    color: #e2e8f0;
    background: transparent;
}

QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 7px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #3b82f6;
}

QPushButton:pressed {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #334155;
    color: #94a3b8;
}

QTableWidget {
    background-color: #172338;
    alternate-background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #334155;
    selection-background-color: #1e40af;
    selection-color: white;
}

QTableWidget::item {
    padding: 8px;
}

QHeaderView::section {
    background-color: #243349;
    color: #94a3b8;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #334155;
    font-weight: 600;
}

QLineEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 7px;
    color: white;
    padding: 10px;
}

QLineEdit:focus {
    border: 1px solid #3b82f6;
}

QScrollBar:vertical {
    background-color: #0f172a;
    width: 10px;
}

QScrollBar::handle:vertical {
    background-color: #475569;
    border-radius: 5px;
    min-height: 20px;
}
"""
