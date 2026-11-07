
import socket
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener


class DiscoveryListener(ServiceListener):
    def __init__(self):
        self.devices = {}

    def add_service(self, zc, service_type, name):
        info = zc.get_service_info(
            service_type, name, timeout=1000
        )

        if not info:
            return

        for ip in info.parsed_addresses():
            if ":" in ip:
                continue

            self.devices.setdefault(ip, []).append({
                "protocol": "mDNS",
                "name": name,
                "service": service_type,
            })

    def update_service(self, zc, service_type, name):
        self.add_service(zc, service_type, name)

    def remove_service(self, zc, service_type, name):
        pass


def discover_mdns(timeout=4):
    listener = DiscoveryListener()

    with Zeroconf() as zc:
        browser = ServiceBrowser(
            zc,
            [
                "_http._tcp.local.",
                "_googlecast._tcp.local.",
                "_airplay._tcp.local.",
                "_ipp._tcp.local.",
                "_workstation._tcp.local.",
            ],
            listener,
        )

        time.sleep(timeout)
        browser.cancel()

    return listener.devices


def discover_ssdp(timeout=3):
    devices = {}
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM,
        socket.IPPROTO_UDP,
    )

    try:
        sock.settimeout(0.5)

        message = (
            "M-SEARCH * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            'MAN: "ssdp:discover"\r\n'
            "MX: 2\r\n"
            "ST: ssdp:all\r\n"
            "\r\n"
        )

        sock.sendto(
            message.encode("ascii"),
            ("239.255.255.250", 1900),
        )

        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            try:
                data, address = sock.recvfrom(8192)
            except socket.timeout:
                continue

            ip = address[0]
            response = data.decode(
                "utf-8", errors="replace"
            )

            devices.setdefault(ip, []).append({
                "protocol": "SSDP",
                "name": "UPnP Device",
                "response": response,
            })

    finally:
        sock.close()

    return devices
