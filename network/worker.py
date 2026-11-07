
from PySide6.QtCore import QThread, Signal

from network.interface import get_network_info
from network.scanner import scan_network
from network.device_enrichment import identify_devices


class ScanWorker(QThread):
    device_found = Signal(dict)
    device_updated = Signal(str, dict)
    network_detected = Signal(dict)
    progress_changed = Signal(str)
    scan_error = Signal(str)

    def run(self):
        try:
            self.progress_changed.emit(
                "Detecting network..."
            )

            network_info = get_network_info()
            self.network_detected.emit(network_info)

            self.progress_changed.emit(
                "Scanning for devices..."
            )

            devices = scan_network(
                subnet=network_info["subnet"],
                gateway=network_info["gateway"],
                local_ip=network_info["local_ip"],
            )

            discovered_ips = set()

            for device in devices:
                discovered_ips.add(device["ip"])
                self.device_found.emit(device)

            self.progress_changed.emit(
                "Identifying devices..."
            )

            identities = identify_devices()

            # Only update devices found in this ARP scan.
            for ip, metadata in identities.items():
                if ip in discovered_ips:
                    self.device_updated.emit(ip, metadata)

            self.progress_changed.emit(
                f"Complete: {len(devices)} devices discovered"
            )

        except Exception as error:
            print(f"[WORKER ERROR] {error}", flush=True)
            self.scan_error.emit(str(error))

        finally:
            print("[WORKER] Finished", flush=True)

