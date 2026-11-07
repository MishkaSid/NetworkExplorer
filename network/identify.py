
import re
import socket
import subprocess

from manuf import manuf


mac_parser = manuf.MacParser()


def get_manufacturer(mac: str) -> str:
    """Get manufacturer from MAC address."""

    try:
        first_byte = int(mac.split(":")[0], 16)

        # Bit 1 indicates a locally administered MAC.
        if first_byte & 0x02:
            return "Private / Randomized MAC"

        vendor = (
            mac_parser.get_comment(mac)
            or mac_parser.get_manuf(mac)
        )

        return vendor or "Unknown Manufacturer"

    except (ValueError, IndexError, TypeError):
        return "Unknown Manufacturer"


def get_device_name(
    ip: str,
    gateway: str,
    local_ip: str,
) -> str:
    """Resolve a device name with a bounded timeout."""

    if ip == gateway:
        return "Router / Default Gateway"

    if ip == local_ip:
        return f"This PC ({socket.gethostname()})"

    try:
        result = subprocess.run(
            ["ping", "-a", "-n", "1", "-w", "500", ip],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=2,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        match = re.search(
            rf"([^\s\[\]]+)\s+\[{re.escape(ip)}\]",
            result.stdout,
            re.IGNORECASE,
        )

        if match:
            hostname = match.group(1)

            if hostname != ip:
                return hostname

    except (subprocess.TimeoutExpired, OSError):
        pass

    return "Unknown Device"
