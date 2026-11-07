
import ipaddress
import json
import subprocess


POWERSHELL_COMMAND = r"""
$routes = @(
    Get-NetRoute -AddressFamily IPv4 `
        -DestinationPrefix '0.0.0.0/0' `
        -ErrorAction Stop |
    Where-Object { $_.NextHop -ne '0.0.0.0' }
)

$candidates = foreach ($route in $routes) {
    $adapter = Get-NetIPInterface `
        -InterfaceIndex $route.InterfaceIndex `
        -AddressFamily IPv4

    $addresses = @(
        Get-NetIPAddress `
            -InterfaceIndex $route.InterfaceIndex `
            -AddressFamily IPv4 |
        Where-Object {
            $_.IPAddress -notlike '169.254.*'
        }
    )

    foreach ($address in $addresses) {
        [PSCustomObject]@{
            interface_alias = $route.InterfaceAlias
            interface_index = $route.InterfaceIndex
            ip = $address.IPAddress
            prefix_length = $address.PrefixLength
            gateway = $route.NextHop
            metric = [int]$route.RouteMetric +
                     [int]$adapter.InterfaceMetric
        }
    }
}

$candidates |
    Sort-Object metric |
    Select-Object -First 1 |
    ConvertTo-Json -Compress
"""


def get_network_info() -> dict:
    """Detect the preferred Windows IPv4 network."""

    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            POWERSHELL_COMMAND,
        ],
        capture_output=True,
        text=True,
        timeout=15,
        check=True,
    )

    if not result.stdout.strip():
        raise RuntimeError(
            "No active IPv4 default gateway was found."
        )

    info = json.loads(result.stdout)

    network = ipaddress.ip_network(
        f"{info['ip']}/{info['prefix_length']}",
        strict=False,
    )

    if not network.is_private:
        raise RuntimeError(
            "Automatic scanning supports private networks only."
        )

    if network.num_addresses > 256:
        raise RuntimeError(
            "Detected subnet is larger than 256 addresses."
        )

    return {
        "interface": info["interface_alias"],
        "interface_index": info["interface_index"],
        "local_ip": info["ip"],
        "subnet": str(network),
        "gateway": info["gateway"],
    }
