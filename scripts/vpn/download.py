import os
import re
import geoip2.database
import urllib.request
from pathlib import Path
from multiprocessing import Pool

CONFIG_DIR = 'config'
DB_URL = "https://git.io/GeoLite2-City.mmdb"
DB_PATH = f"{CONFIG_DIR}/{DB_URL.split('/')[-1]}"


def download_db():
    urllib.request.urlretrieve(DB_URL, DB_PATH)


def download_file(url):
    filename = f"{CONFIG_DIR}/{url.split('/')[-1]}"
    urllib.request.urlretrieve(url, f"{CONFIG_DIR}/{url.split('/')[-1]}")
    return filename


def delete(filename):
    os.remove(filename)


def multidelete(filenames):
    with Pool() as p:
        return p.map(delete, filenames)


def geolocate(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('remote '):
                break
        ip = line.split(' ')[1]
        with geoip2.database.Reader(DB_PATH) as reader:
            response = reader.city(ip)
            return response.city.names['en']


def get_servers():
    with open('scripts/vpn/nordvpn.html') as file:
        content = file.read()
        matches = re.findall(
            r'https:\/\/downloads.nordcdn.com\/configs\/files\/ovpn_tcp\/servers\/us\d+.nordvpn.com.tcp.ovpn', content)
        with Pool() as p:
            return p.map(download_file, matches)


def multigeolocate(servers):
    with Pool() as p:
        return p.map(geolocate, servers)


if __name__ == '__main__':
    Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
    db_path = download_db()
    servers = get_servers()
    locations = multigeolocate(servers)
    far_servers = [server for server, location in zip(
        servers, locations
    ) if location not in {'Miami', 'Atlanta'}]
    multidelete(far_servers)
    delete(DB_PATH)
