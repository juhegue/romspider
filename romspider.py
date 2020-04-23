# -*- coding: utf-8 -*-
# @Juhegue
# jue abr 23 08:29:55 CEST 2020

import os
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import requests
import re
import urllib3

PLANETEMU = [
    'atari-2600',
    'atari-5200',
    'atari-7800',
    'coleco-colecovision',
    'sega-game-gear',
    'mattel-intellivision',
    'atari-jaguar',
    'atari-lynx',
    'sega-master-system',
    'sega-mega-drive',
    'snk-neo-geo-pocket',
    'snk-neo-geo-cd-world',
    'mame-roms',
    'nec-pc-engine',
    'sony-playstation-games-europe',
    'panasonic-3do-interactive-multiplayer-games',  # No van en la raspberry PI
]


class Soup(object):

    def __call__(self, *args, **kwargs):
        url = kwargs.get('url')

        # Ignora error de certificado SSL
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        html = urllib.request.urlopen(url, context=ctx).read()
        return BeautifulSoup(html, 'html.parser')


class PlanetemuSpider(object):

    def __init__(self, web, url, sufijo, path):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        suop = Soup()
        sopa = suop(url=web + url)
        hrefs = list()
        for tag in sopa('a'):
            href = tag.get('href', None)
            if href and href.startswith(sufijo):
                hrefs.append(href)

        for n, href in enumerate(hrefs):
            print('[{:03d}-{:03d}]{}'.format(len(hrefs), n, href), end='')
            try:
                sopa = suop(url=web + href)
                action = sopa.find('form', {'name': 'MyForm'}).get('action')
                id = sopa.find('input', {'name': 'id'}).get('value')
                download = sopa.find('input', {'name': 'download'}).get('value')

                data = {
                    'id': id,
                    'download': download,
                }
                form = web + action
                with requests.post(form, data=data, verify=False, stream=True) as response:
                    response.raise_for_status()
                    content = response.headers.get('content-disposition')

                    name = None
                    if content:
                        name = re.findall("filename=(.+)", content)
                        if name:
                            name = name[0].replace('"', '')

                    if not name:
                        name = href.split('/')[-1] + '.zip'

                    fname = os.path.join(path, name)
                    if not os.path.isfile(fname):
                        with open(fname, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=10024):
                                if chunk:
                                    f.write(chunk)

                    print(':', name)
            except:
                print(': ERROR')


if __name__ == '__main__':
    web = 'https://www.planetemu.net'

    for rom in PLANETEMU:
        if not os.path.isdir(rom):
            os.mkdir(rom)

        url = '/roms/{}'.format(rom)
        sufijo = '/rom/{}'.format(rom)
        PlanetemuSpider(web, url, sufijo, rom)

