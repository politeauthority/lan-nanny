"""Parse NMap
Tools for reading and traversing nmap output files.

"""
from collections import OrderedDict
import logging
import xml

import xmltodict


def parse_xml(phile: str, scan_type:str):
    try:
        phile = open(phile, "r")
        parsed = xmltodict.parse(phile.read())
    except xml.parsers.expat.ExpatError:
        logging.error('Error reading xml: %s' % phile)
        return False

    if scan_type == 'hosts':
        return parse_hosts(parsed)
    elif scan_type == 'ports':
        return parse_ports(parsed)
    else:
        logging.error('Error, unsure what type of NMAP file to parse.')
        exit(1)
        return False


def parse_hosts(parsed: dict):
    """Parses an NMAP output file and returns relevant host information."""
    hosts = []
    if 'host' not in parsed['nmaprun']:
        print('No hosts found, this could be a configuration error.')
        return []
    for host in parsed['nmaprun']['host']:
        # Check if this host is the localhost and skip
        is_local_host = _detect_local_host(host)

        found = {
            'ip': _get_host_ip(host),
            'mac': _get_host_mac(host),
            'vendor': _get_host_vendor(host),
            'hostname': _get_host_hostname(host)
        }
        hosts.append(found)

    return hosts


def _detect_local_host(host: dict) -> bool:
    """Detects if the host is the localhost since the xml makeup is different for the localhost."""
    if host['status']['@state'] == 'up' and host['status']['@reason'] == 'localhost-response':
        return True
    return False


def _get_host_ip(host: dict) -> str:
    """Get the host's IPV4 address from the parsed XML scan."""
    if 'address' not in host:
        return ''

    host_ip = ''

    if isinstance(host['address'], OrderedDict):
        host_ip = host['address']['@addr']
        return host_ip

    for addr in host['address']:
        if '@addrtype' not in addr:
            continue

        if addr['@addrtype'] == 'ipv4':
            host_ip = addr['@addr']
            break

    return host_ip


def _get_host_mac(host: dict) -> str:
    """Get the host's MAC address from the parsed XML scan."""
    if 'address' not in host:
        return ''

    host_vendor = ''

    if isinstance(host['address'], OrderedDict):
        return ''

    for addr in host['address']:
        if '@addrtype' not in addr:
            continue
        if addr['@addrtype'] == 'mac':
            host_vendor = addr['@addr']
            break

    return host_vendor


def _get_host_vendor(host: dict) -> str:
    """Get the host's vendor from the parsed XML scan."""
    if 'address' not in host:
        return ''

    host_vendor = ''
    for addr in host['address']:
        if '@vendor' not in addr:
            continue
        host_vendor = addr['@vendor']
        break

    return host_vendor


def _get_host_hostname(host: dict) -> str:
    """Get the host's hostname, if available."""
    if 'hostnames' not in host or not host['hostnames']:
        return ''
    return host['hostnames']['hostname']['@name']


def parse_ports(parsed):
    """Parse an NMap output file for port data, returning the relevant info."""
    if 'host' not in parsed['nmaprun']:
        logging.error('\t\tNo data in parsed Nmap')
        return False

    if 'ports' not in parsed['nmaprun']['host']:
        logging.error('\t\tNo host in Nmap parsed scan')
        return False

    if not isinstance(parsed['nmaprun']['host']['ports'], OrderedDict):
        logging.error('\t\tCannot parse Nmap port file.')
        logging.error("\t\t%s" % parsed['nmaprun']['host']['ports'])
        return False

    prestine_ports = []

    # If the scan returned but has no actionable ports return
    if 'port' not in parsed['nmaprun']['host']['ports']:
        logging.warning('No usable ports from NMAP scan')
        return prestine_ports

    raw_ports = parsed['nmaprun']['host']['ports']['port']
    if not isinstance(raw_ports, list):
        raw_ports = [raw_ports]

    for raw_port in raw_ports:
        found = {
            'number': _get_port_number(raw_port),
            'protocol': _get_port_protocol(raw_port),
            'state': _get_port_state(raw_port),
            'service': _get_port_service(raw_port),
        }
        if found['number'] == '':
            logging.warning('Found invalid port, skipping')
            continue
        prestine_ports.append(found)


    return prestine_ports


def _get_port_number(port: dict) -> int:
    """Get the port's number from the parsed XML scan."""
    if '@portid' not in port:
        return ''
    try:
        if type(port['@portid']) == str:
            return int(port['@portid'])
    except TypeError:
        return ''
    return ''


def _get_port_protocol(port: dict) -> str:
    """Get the port's protocol from the parsed XML scan."""
    if '@protocol' not in port:
        return ''
    if type(port) == str:
        return ''
    return port['@protocol']


def _get_port_state(port: dict) -> str:
    """Get the port's state from the parsed XML scan."""
    if 'state' not in port:
        return False
    if isinstance(port['state'], str):
        logging.warning('No useable port state in parsed nmap')
        return False
    if not isinstance(port['state']['@state'], str):
        # @todo: revisit this!
        logging.error('No useable port state in parsed nmap')
        return False
    if port['state']['@state'] == 'open':
        return 'open'


def _get_port_service(port: dict) -> str:
    """Get the port's service from the parsed XML scan."""
    if 'service' not in port:
        return ''
    service_name = ''
    if '@name' in port['service']:
        service_name = port['service']['@name']
    return service_name


# End File: lan-nanny/lan_nanny/modules/scanning/parse_nmap.py
