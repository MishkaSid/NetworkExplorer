
import ipaddress

from scapy.all import ARP, Ether, srp
from network.identify import (
    get_device_name,
    get_manufacturer,
)

def scan_network(
    subnet: str,
    gateway: str,
    local_ip: str,
) -> list[dict]:
    """Discover devices and identify the default gateway."""

    network = ipaddress.ip_network(
        subnet,
        strict=False,
    )

    if network.version != 4 or not network.is_private:
        raise ValueError("Only private IPv4 networks are supported.")

    if network.num_addresses > 256:
        raise ValueError("Subnet exceeds the 256-address limit.")

    if ipaddress.ip_address(gateway) not in network:
        raise ValueError(
            "Default gateway is outside the selected subnet."
        )

    print(f"[SCAN] Scanning {network}", flush=True)
    print(f"[SCAN] Gateway: {gateway}", flush=True)

    packet = (
        Ether(dst="ff:ff:ff:ff:ff:ff")
        / ARP(pdst=str(network))
    )

    answered, _ = srp(
        packet,
        timeout=2,
        retry=0,
        verbose=False,
    )

    devices = []
    seen_ips = set()

    for _, response in answered:
        ip = response.psrc

        if ip in seen_ips:
            continue

        seen_ips.add(ip)

        is_gateway = ip == gateway

        devices.append({
            "hostname": get_device_name(
                ip=ip,
                gateway=gateway,
                local_ip=local_ip,
            ),
            "manufacturer": get_manufacturer(
                response.hwsrc
            ),
            "ip": ip,
            "mac": response.hwsrc,
            "status": "Online",
            "is_gateway": ip == gateway,
        })


    devices.sort(
        key=lambda device: (
            not device["is_gateway"],
            ipaddress.ip_address(device["ip"]),
        )
    )

    print(
        f"[SCAN] Found {len(devices)} devices",
        flush=True,
    )

    return devices
