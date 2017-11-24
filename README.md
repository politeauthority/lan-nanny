# LAN Nanny
A tool for collecting and storing network devices by mac/ip and tagging the devices with custom naming.

## Example Usage
This will scan the entire range of ips given. When running regular scans, its best to target the expect DCHP ranges, if you're interested in units coming on and dropping off network.
```
sudo python lan_nanny.py --ip=192.168.1.1-255
```

## Install
- You'll need the utility NMAP and the python-mysql connector
- Then run install/create_tables.sql