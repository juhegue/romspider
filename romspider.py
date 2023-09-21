#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Juhegue
# jue abr 23 08:29:55 CEST 2020
# jue 21 sep 2023 08:33:32 CEST

import os
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
import re
import urllib3
import zipfile

PLANETEMU = [
    'atari-2600',
    'atari-5200',
    'atari-7800',
    'colecovision',
    'game-boy',
    'game-gear',
    'gba',
    'intellivision',
    'jaguar',
    'lynx',
    'master-system',
    'mega-drive',
    'neo-geo-pocket',
    'neo-geo-cd',
    'nes',
    'nintendo-64',
    'odyssey',
    'pc-engine',
    'playstation',
    'saturn',
    'super-nes',
    'virtual-boy',
    'wonderswan',
    'mame',
    'non-mame',
]


class Soup(object):

    def __call__(self, *args, **kwargs):
        url = kwargs.get('url')
        req = Request(
            url=url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        html = urlopen(req).read()
        return BeautifulSoup(html, 'html.parser')


class PlanetemuSpider(object):

    def __call__(self, web, url, sufijo, path):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        weburl = web + url
        suop = Soup()
        sopa = suop(url=weburl)
        hrefs = list()
        for tag in sopa('a'):
            href = tag.get('href', None)
            if href and href.startswith('/roms/'):
                hrefs.append(href)

        for m, hrefrom in enumerate(hrefs):
            fname = None

            webhref = web + hrefrom
            sopa = suop(url=webhref)

            sufijorom = hrefrom.replace('roms', 'rom')
            roms = list()
            for tag in sopa('a'):
                href = tag.get('href', None)
                if href and href.startswith(sufijorom):
                    roms.append(href)

            print('[{:04d}-{:03d}]{}'.format(len(roms), m+1, hrefrom))

            for n, href in enumerate(roms):
                webform = web + href
                formsopa = suop(url=webform)
                try:
                    name = None
                    action = formsopa.find('form', {'name': 'MyForm'}).get('action')
                    id = formsopa.find('input', {'name': 'id'}).get('value')
                    download = formsopa.find('input', {'name': 'download'}).get('value')

                    data = {
                        'id': id,
                        'download': download,
                    }
                    form = web + action
                    with requests.post(form, data=data, verify=False, stream=True) as response:
                        response.raise_for_status()
                        content = response.headers.get('content-disposition')

                        if content:
                            name = re.findall("filename=(.+)", content)
                            if name:
                                name = name[0].replace('"', '')

                        if not name:
                            name = href.split('/')[-1] + '.zip'

                        if m == 0 and not os.path.isdir(path):
                            os.mkdir(rom)

                        fname = os.path.join(path, name)
                        if not os.path.isfile(fname):
                            with open(fname, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=10240):
                                    if chunk:
                                        f.write(chunk)
                            if not zipfile.is_zipfile(fname):
                                os.remove(fname)
                                name += ' corrupto'
                        print('  [{:04d}] {}'.format(n + 1, name))

                except KeyboardInterrupt:
                    if fname and os.path.isfile(fname):
                        os.remove(fname)
                    return False

                except Exception as e:
                    if fname and os.path.isfile(fname):
                        os.remove(fname)

                    print(f'{e}  ERROR')

        return True


if __name__ == '__main__':
    web = 'https://www.planetemu.net'

    for rom in PLANETEMU:
        url = '/machine/{}'.format(rom)
        sufijo = '/roms/{}'.format(rom)
        spider = PlanetemuSpider()
        if not spider(web, url, sufijo, rom):
            break

