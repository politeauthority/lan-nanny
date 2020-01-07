from modules.scanning import parse_nmap


def test():
    """
    """
    ports = parse_nmap.parse_ports('/home/pi/repos/lan-nanny/lan_nanny/port_scan_9.xml')
    print(ports)


if __name__ == '__main__':
    # args = parse_args()
    # Scan(args).run()
    test()