"""Parse Arp

"""


def parse_hosts(raw_arp: str) -> list:
    lines = raw_arp.decode().split('\n')
    if len(lines) <= 2:
        return []

    hosts = []
    for line in lines[2:]:
        host_details = line.split('\t')
        if len(host_details) < 3:
            continue
        found = {}
        found['ip'] = host_details[0]
        found['mac'] = host_details[1]
        found['vendor'] = host_details[2]
        if 'unknown' in found['vendor'].lower():
            found['vendor'] = None
        hosts.append(found)
    return hosts


# End File: lan-nanny/lan_nanny/modules/scanning/parse_arp.py
