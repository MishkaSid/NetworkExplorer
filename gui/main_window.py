
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtWidgets import QInputDialog
from data.database import get_custom_name, save_custom_name
from network.worker import ScanWorker


class NetworkExplorer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.worker = None
        self.scan_failed = False

        self.setWindowTitle("Network Explorer")
        self.resize(1000, 650)

        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        title = QLabel("Network Explorer")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )
        layout.addWidget(title)

        # Network information
        self.network_label = QLabel(
            "Network: Not detected"
        )
        self.gateway_label = QLabel(
            "Default Gateway: Not detected"
        )
        self.interface_label = QLabel(
            "Adapter: Not detected"
        )

        layout.addWidget(self.network_label)
        layout.addWidget(self.gateway_label)
        layout.addWidget(self.interface_label)

        # Scan controls
        controls = QHBoxLayout()

        self.status_label = QLabel("Ready to scan")
        controls.addWidget(self.status_label)
        controls.addStretch()

        self.scan_button = QPushButton("Scan Network")
        self.scan_button.clicked.connect(self.start_scan)
        controls.addWidget(self.scan_button)

        layout.addLayout(controls)

        # Device table
        self.device_table = QTableWidget(0, 6)

        self.device_table.setHorizontalHeaderLabels([
            "Device Name",
            "IP Address",
            "MAC Address",
            "Manufacturer",
            "Model",
            "Status",
        ])

        self.device_table.setHorizontalHeaderLabels([
            "Device Name",
            "IP Address",
            "MAC Address",
            "Manufacturer",
            "Status",
        ])
        self.device_table.setAlternatingRowColors(True)
        self.device_table.setShowGrid(False)
        self.device_table.verticalHeader().setVisible(False)
        self.device_table.verticalHeader().setDefaultSectionSize(44)
        self.device_table.setSortingEnabled(True)

        self.device_table.setHorizontalHeaderLabels([
            "Device Name",
            "IP Address",
            "MAC Address",
            "Status",
        ])
        self.device_table.cellDoubleClicked.connect(
        self.rename_device
    )

        self.device_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.device_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.device_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        layout.addWidget(self.device_table)

    def start_scan(self):
        if self.worker is not None:
            return

        self.device_table.setRowCount(0)
        self.scan_failed = False

        self.status_label.setText(
            "Detecting network and scanning..."
        )
        self.scan_button.setEnabled(False)

        self.worker = ScanWorker()

        self.worker.network_detected.connect(
            self.update_network_info
        )
        self.worker.device_found.connect(
            self.add_device
        )
        self.worker.scan_error.connect(
            self.show_error
        )
        self.worker.finished.connect(
            self.scan_finished
        )
        self.worker.device_updated.connect(
            self.update_device
        )

        self.worker.progress_changed.connect(
            self.status_label.setText
)

        self.worker.start()

    def update_network_info(self, info):
        self.network_label.setText(
            f"Network: {info['subnet']} "
            f"(Local IP: {info['local_ip']})"
        )

        self.gateway_label.setText(
            f"Default Gateway: {info['gateway']}"
        )

        self.interface_label.setText(
            f"Adapter: {info['interface']}"
        )
        self.gateway_ip = info["gateway"]

        self.status_label.setText("Scanning devices...")

    def add_device(self, device):
        row = self.device_table.rowCount()
        self.device_table.insertRow(row)
        was_sorting = self.device_table.isSortingEnabled()
        self.device_table.setSortingEnabled(False)

        values = [
            get_custom_name(device["mac"])
            or device["hostname"],
            device["ip"],
            device["mac"],
            device.get("manufacturer", "Unknown"),
            device.get("model", "Unknown"),
            device["status"],
        ]
        
        custom_name = get_custom_name(device["mac"])

        if custom_name:
            values[0] = custom_name

        for column, value in enumerate(values):
            item = QTableWidgetItem(value)

            if device["is_gateway"]:
                item.setBackground(QColor("#164e3e"))
                item.setForeground(QColor("#ffffff"))

            self.device_table.setItem(
                row,
                column,
                item,
            )
        self.device_table.setSortingEnabled(was_sorting)

    def show_error(self, message):
        self.scan_failed = True
        self.status_label.setText("Scan failed")

        QMessageBox.warning(
            self,
            "Network Scan Error",
            message,
        )

    def scan_finished(self):
        self.scan_button.setEnabled(True)

        if not self.scan_failed:
            count = self.device_table.rowCount()
            self.status_label.setText(
                f"Scan completed: {count} devices discovered"
            )

        self.worker = None

    def rename_device(self, row, column):
        name_item = self.device_table.item(row, 0)
        mac_item = self.device_table.item(row, 2)

        if not name_item or not mac_item:
            return

        current_name = name_item.text()
        mac = mac_item.text()

        new_name, accepted = QInputDialog.getText(
            self,
            "Rename Device",
            f"Enter a name for {mac}:",
            text=current_name,
        )

        if not accepted:
            return

        new_name = new_name.strip()

        if not new_name:
            return

        if len(new_name) > 80:
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Device names cannot exceed 80 characters.",
            )
            return

        save_custom_name(mac, new_name)
        name_item.setText(new_name)
    
    
    def update_device(self, ip: str, metadata: dict):
        table = self.device_table

        was_sorting = table.isSortingEnabled()
        table.setSortingEnabled(False)

        try:
            for row in range(table.rowCount()):
                ip_item = table.item(row, 1)

                if not ip_item or ip_item.text() != ip:
                    continue

                name_item = table.item(row, 0)
                mac_item = table.item(row, 2)

                if not name_item or not mac_item:
                    break

                current_name = name_item.text()
                mac = mac_item.text()

                # Never overwrite manually saved names.
                custom_name = get_custom_name(mac)

                is_gateway = ip == getattr(
                    self, "gateway_ip", None
                )

                discovered_name = metadata.get("name")

                if (
                    not custom_name
                    and not is_gateway
                    and discovered_name
                    and (
                        current_name == "Unknown Device"
                        or current_name.startswith("Unknown")
                    )
                ):
                    name_item.setText(discovered_name)

                manufacturer = metadata.get("manufacturer")
                model = metadata.get("model")

                if manufacturer:
                    table.setItem(
                        row, 3,
                        QTableWidgetItem(manufacturer)
                    )

                if model:
                    table.setItem(
                        row, 4,
                        QTableWidgetItem(model)
                    )

                break

        finally:
            table.setSortingEnabled(was_sorting)

