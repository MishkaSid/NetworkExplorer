
import ipaddress
from urllib.parse import urlsplit
from defusedxml import ElementTree as ET

import requests


MAX_XML_BYTES = 128 * 1024


def get_header(response: str, header: str) -> str | None:
    """Read one HTTP-style SSDP header."""
    prefix = header.lower() + ":"

    for line in response.splitlines():
        if line.lower().startswith(prefix):
            return line.split(":", 1)[1].strip()

    return None


def get_xml_description(url: str, device_ip: str) -> dict:
    """Retrieve a description from the responding LAN device."""

    parsed = urlsplit(url)

    if parsed.scheme != "http":
        return {}

    if parsed.username or parsed.password:
        return {}

    try:
        address = ipaddress.ip_address(parsed.hostname or "")
        expected = ipaddress.ip_address(device_ip)

        if address.version != 4 or address != expected:
            return {}

        if not address.is_private:
            return {}

        if parsed.port is None:
            port = 80
        else:
            port = parsed.port

        if not 1 <= port <= 65535:
            return {}

    except (ValueError, TypeError):
        return {}

    try:
        # Avoid using proxy settings for local device requests.
        with requests.Session() as session:
            session.trust_env = False

            with session.get(
                url,
                timeout=(1.5, 2.5),
                allow_redirects=False,
                stream=True,
            ) as response:

                response.raise_for_status()

                if response.status_code != 200:
                    return {}

                content = bytearray()

                for chunk in response.iter_content(
                    chunk_size=4096
                ):
                    content.extend(chunk)

                    if len(content) > MAX_XML_BYTES:
                        return {}

        root = ET.fromstring(bytes(content))

        fields = {
            "friendlyName": "name",
            "manufacturer": "manufacturer",
            "modelName": "model",
            "deviceType": "device_type",
        }

        result = {}

        # Namespace-independent element lookup.
        for element in root.iter():
            tag = element.tag.split("}")[-1]

            if tag in fields and element.text:
                key = fields[tag]

                if key not in result:
                    result[key] = element.text.strip()[:200]

        return result

    except (
        requests.RequestException,
        ET.ParseError,
        OSError,
        ValueError,
    ):
        return {}
