# LAN Nanny
LAN Nanny is a tool for local network device/port discovery and monitoring. Lots of routers
masquerade users into thinking they have this functionality, but its broken, slow or wrong.
LAN Nanny attempts to provide the user with a local, secure, web app to visualize all devices on a 
network, as well as give a user a quick glance to a full networks worth of actively open ports, 
either by port number, type or device currently advertising the exposed port.

## Install
###  Via Docker
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
    -v /home/pi/data/mysql:/var/lib/mysql \
    --network host \
    --restart=always \
    -p 3306:3306 \
    -d \
    mysql:latest
```
After creating the MySQL container, create the Lan Nanny database and user.
```
mysql -h 127.0.0.1 -u root -p{password_you_chose}
CREATE DATABASE IF NOT EXISTS lan_nanny;
CREATE USER 'lan_nanny'@'%' IDENTIFIED BY '{password_for_lan_nanny}';
GRANT ALL PRIVILEGES ON  lan_nanny. * TO 'lan_nanny'@'%';
```

Then create the Lan Nanny container
```console
docker run \
    --name lan-nanny \
    -e LAN_NANNY_DB_PASS=my_password \
    --net=host \
    -d \
    --rm \
    lan-nanny
```

## Development
Development is easiest via Docker. This assumes you already have a MySQL container running.
It takes about 30 minutes to build the base docker image, and then another x to build the development image from scratch, or you can just pull the development image from docker hub at `politeauthority/lan-nanny:dev-latest`.
```
docker build . -f dev.Dockerfile -t="lan-nanny:dev"
docker run \
    --name lan-nanny-dev \
    -v /path/to/lan-nanny:/app \
    -e LAN_NANNY_DB_USER=root \
    -e LAN_NANNY_DB_PASS=my_password \
    --net=host \
    -d \
    --rm \
    lan-nanny:dev
```

### Testing
The easiest way to properly run the Lan Nanny test suite is via docker.
```console
docker build -t lan-nanny .
docker run \
    -v your-repos/lan-nanny:/app2 \
    lan-nanny
```