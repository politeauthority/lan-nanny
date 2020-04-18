# LAN Nanny
LAN Nanny is a tool for local network device/port discovery and monitoring. Lots of routers
masquerade users into thinking they have this functionality, but its broken, slow or wrong.
LAN Nanny attempts to provide the user with a local, secure, web app to visualize all devices on a 
network, as well as give a user a quick glance to a full networks worth of actively open ports, 
either by port number, type or device currently advertising the exposed port.

## Install
```console
git clone git@github.com:politeauthority/lan-nanny.git
cd lan-nanny/
python3 install-upgrade.py
```

## Testing
The easiest way to properly run the Lan Nanny test suite is via docker.
```console
docker build -t lan-nanny .
docker run \
    -v your-repos/lan-nanny:/app2 \
    lan-nanny
```