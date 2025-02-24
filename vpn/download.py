import os
import shutil
from glob import glob
from zipfile import ZipFile
import geoip2.database
import urllib.request
from pathlib import Path
from multiprocessing import Pool

CONFIG_DIR = 'config'
DB_URL = "https://git.io/GeoLite2-City.mmdb"
DB_PATH = f"{CONFIG_DIR}/{DB_URL.split('/')[-1]}"
VPN_DIR = 'ovpn'
TCP_DIR = 'ovpn_tcp'
VPN_EXT = 'zip'
ZIP_FN = f'{VPN_DIR}.{VPN_EXT}'
ZIP_PATH = os.path.join(CONFIG_DIR, ZIP_FN)
UNZIP_PATH = os.path.join(CONFIG_DIR, VPN_DIR)


def download_db():
    urllib.request.urlretrieve(DB_URL, DB_PATH)


def download_file(url):
    filename = os.path.join(CONFIG_DIR, url.split('/')[-1])
    urllib.request.urlretrieve(url, filename)
    return filename


def delete(path):
    if os.path.isfile(path):
        return os.remove(path)
    elif os.path.isdir(path):
        return shutil.rmtree(path)
    else:
        raise Exception('Path to delete does not exist.')


def multidelete(paths):
    with Pool() as p:
        return p.map(delete, paths)


def geolocate(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('remote '):
                break
        ip = line.split(' ')[1]
        with geoip2.database.Reader(DB_PATH) as reader:
            response = reader.city(ip)
            return response.city.names.get('en')


def move(cfg):
    return shutil.move(cfg, CONFIG_DIR)


def get_servers():
    download_file(
        f'https://downloads.nordcdn.com/configs/archives/servers/{ZIP_FN}')
    with ZipFile(ZIP_PATH, 'r') as zf:
        zf.extractall(UNZIP_PATH)
    # only use American servers
    cfgs = glob(os.path.join(UNZIP_PATH, TCP_DIR, 'us*.tcp.ovpn'))
    with Pool() as p:
        return p.map(move, cfgs)


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
    multidelete(far_servers + [DB_PATH, ZIP_PATH, UNZIP_PATH])
