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

### Docker via install
You can install and run docker on a Raspberry PI with the following command.
```console
curl -sSL https://get.docker.com | sh
```

This section will be simplified with docker-compose in the near future.
Then install a MySQL server
```console
docker run \
    --name lan-nanny-mysql \
    -e MYSQL_ROOT_PASSWORD=my_password \
    -p 3306:3306 \
    -d \
    mysql:latest
```

Then create the Lan Nanny container
```console
docker run \
    --name lan-nanny \
    -p 5000:5000 \
    -e LAN_NANNY_DB_PASS=my_password \
    --link lan-nanny-mysql \
    -d \
    --rm \
    lan-nanny
```

## Development
Development is easiest via Docker. This assumes you already have a MySQL container running.
```
docker build -t lan_nanny .
docker run \
    --name lan-nanny \
    -v /path/to/lan-nanny:/app \
    -p 5000:5000 \
    -e LAN_NANNY_DB_USER=root \
    -e LAN_NANNY_DB_PASS=my_password \
    --link lan-nanny-mysql \
    -d \
    --rm \
    lan-nanny
```

### Testing
The easiest way to properly run the Lan Nanny test suite is via docker.
```console
docker build -t lan-nanny .
docker run \
    -v your-repos/lan-nanny:/app2 \
    lan-nanny
```