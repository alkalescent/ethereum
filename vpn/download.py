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
            return response.city.names['en']


def move(cfg):
    return shutil.move(cfg, CONFIG_DIR)


def get_servers():
    # full_path = os.path.realpath(__file__)
    # curr_dir = os.path.dirname(full_path)
    # with open(os.path.join(curr_dir, 'nordvpn.html')) as file:
    #     content = file.read()
    #     matches = re.findall(
    #         r'https:\/\/downloads.nordcdn.com\/configs\/files\/ovpn_tcp\/servers\/us\d+.nordvpn.com.tcp.ovpn', content)
    #     with Pool() as p:
    #         return p.map(download_file, matches)

    # NEW
    VPN_DIR = 'ovpn'
    TCP_DIR = 'ovpn_tcp'
    VPN_EXT = 'zip'
    ZIP_FN = f'{VPN_DIR}.{VPN_EXT}'
    ZIP_PATH = os.path.join(CONFIG_DIR, ZIP_FN)
    VPN_DIR = os.path.join(CONFIG_DIR, VPN_DIR)
    download_file(
        f'https://downloads.nordcdn.com/configs/archives/servers/{ZIP_FN}')
    with ZipFile(ZIP_PATH, 'r') as zf:
        zf.extractall(VPN_DIR)
    # cfgs = os.listdir(os.path.join(VPN_DIR, TCP_DIR))
    cfgs = glob(os.path.join(VPN_DIR, TCP_DIR, '*.tcp.ovpn'))
    with Pool() as p:
        return p.map(move, cfgs)


def multigeolocate(servers):
    with Pool() as p:
        return p.map(geolocate, servers)


if __name__ == '__main__':
    Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
    # db_path = download_db()
    servers = get_servers()
    # locations = multigeolocate(servers)
    # far_servers = [server for server, location in zip(
    #     servers, locations
    # ) if location not in {'Miami', 'Atlanta'}]
    # multidelete(far_servers)
    # delete(DB_PATH)
