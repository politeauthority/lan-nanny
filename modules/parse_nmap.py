import xmltodict

def parse_hosts(phile):
    """
    Parses an NMAP output file and returns relevant host information.

    """
    phile = open(phile, "r") 
    parsed = xmltodict.parse(phile.read())

    hosts = []
    for host in parsed['nmaprun']['host']:
        # Check if this host is the localhost and skip
        is_local_host = _detect_local_host(host)
        if is_local_host:
            continue

        found = {
            'ip': _get_host_ip(host),
            'mac': _get_host_mac(host),
            'vendor': _get_host_vendor(host)
        }
        hosts.append(found)

    return hosts

def _detect_local_host(host: dict) -> bool:
    """
    Detects if the host is the localhost since the xml makeup is different for the localhost.

    """
    if host['status']['@state'] == 'up' and host['status']['@reason'] == 'localhost-response':
        return True
    return False

def _get_host_ip(host: dict) -> str:
    """
    Gets the host's IPV4 address from the parsed XML scan.

    """
    if 'address' not in host:
        return ''

    host_ip = ''
    for addr in host['address']:
        if '@addrtype' not in addr:
            continue
        if addr['@addrtype'] == 'ipv4':
            host_ip = addr['@addr']
            break

    return host_ip

def _get_host_mac(host: dict) -> str:
    """
    Gets the host's MAC address from the parsed XML scan.

    """
    if 'address' not in host:
        return ''

    host_vendor = ''
    for addr in host['address']:
        if '@addrtype' not in addr:
            continue
        if addr['@addrtype'] == 'mac':
            host_vendor = addr['@addr']
            break

    return host_vendor

def _get_host_vendor(host: dict) -> str:
    """
    Gets the host's vendor from the parsed XML scan.

    """
    if 'address' not in host:
        return ''

    host_vendor = ''
    for addr in host['address']:
        if '@vendor' not in addr:
            continue
        host_vendor = addr['@vendor']
        break

    return host_vendor

def parse_ports(phile):
    """
    Parses an NMap output file for port data, returning the relevant info.

    """
    phile = open(phile, "r") 
    parsed = xmltodict.parse(phile.read())

# End File: lan-nanny/modules/parse_nmap.py
