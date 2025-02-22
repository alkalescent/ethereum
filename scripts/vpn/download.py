import os
import re
import geoip2.webservice
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


def geolocate_server(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('remote '):
                break
        ip = line.split(' ')[1]
        with geoip2.webservice.Client(10, 'license_key', host='geolite.info') as client:
            response = client.city(ip)
            print('city', response)
            print(response.city.iso_code)


def download_configs():
    with open('scripts/vpn/nordvpn.html') as file:
        content = file.read()
        matches = re.findall(
            r'https:\/\/downloads.nordcdn.com\/configs\/files\/ovpn_tcp\/servers\/us\d+.nordvpn.com.tcp.ovpn', content)
        with Pool() as p:
            return p.map(download_file, matches)


def geolocate_servers(config_files):
    with Pool() as p:
        return p.map(geolocate_server, config_files)


if __name__ == '__main__':
    Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
    db_path = download_db()
    # filenames = download_configs()
    filenames = [f'{CONFIG_DIR}/{fn}' for fn in os.listdir(CONFIG_DIR)][:1]
    geolocate_servers(filenames)
