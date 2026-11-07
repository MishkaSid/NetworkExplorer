
from network.service_discovery import (
    discover_mdns,
    discover_ssdp,
)
from network.device_description import (
    get_header,
    get_xml_description,
)


def identify_devices() -> dict:
    """Discover metadata advertised on the local network."""

    results = {}

    print("[IDENTIFY] Discovering SSDP devices...", flush=True)

    ssdp_devices = discover_ssdp(timeout=3)

    for ip, services in ssdp_devices.items():
        description = {}
        server = ""
        device_types = set()
        urls = set()

        for service in services:
            raw = service.get("response", "")

            server = get_header(raw, "SERVER") or server

            service_type = get_header(raw, "ST")

            if service_type:
                device_types.add(service_type)

            location = get_header(raw, "LOCATION")

            if location:
                urls.add(location)

        # A device may advertise multiple services using
        # the same description URL. Fetch each URL once.
        for url in sorted(urls)[:5]:
            metadata = get_xml_description(url, ip)

            for key, value in metadata.items():
                if value and not description.get(key):
                    description[key] = value

        if not description.get("name"):
            if "Samsung" in server:
                description["name"] = "Samsung Media Device"
                description["manufacturer"] = "Samsung"

            elif any(
                "InternetGatewayDevice" in t
                for t in device_types
            ):
                description["name"] = "Internet Gateway"

            elif any(
                "WFADevice" in t
                for t in device_types
            ):
                description["name"] = "Wi-Fi Device"

        description["discovery_source"] = "SSDP"

        if server:
            description["server"] = server

        if device_types:
            description["services"] = sorted(device_types)

        results[ip] = description

    print("[IDENTIFY] Discovering mDNS services...", flush=True)

    mdns_devices = discover_mdns(timeout=4)

    for ip, services in mdns_devices.items():
        existing = results.setdefault(ip, {})

        service_names = [
            service.get("name", "")
            for service in services
        ]

        existing["mdns_services"] = service_names

        # Do not overwrite more specific SSDP names.
        if not existing.get("name"):
            for service in services:
                name = service.get("name", "")

                if name:
                    existing["name"] = name.split("._")[0]
                    existing["discovery_source"] = "mDNS"
                    break

    print(
        f"[IDENTIFY] Identified {len(results)} IPs",
        flush=True,
    )

    return results
