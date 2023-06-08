#!/usr/bin/env python3
from helper import *
from args import parse_arguments
from html import unescape
from random import random
from time import sleep
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from shutil import copy
import requests

requests.packages.urllib3.disable_warnings()


def clean_filename(s: str) -> str:
    keep = ' .!_[]()'
    s = ''.join(c for c in s if c.isalnum() or c in keep)
    return re.sub(r'\s{2,}', ' ', s).strip()


def mkdir(path):
    Path(path).mkdir(exist_ok=True, parents=True)


def get(s, url, stream=False):
    sleep(random() * .8)
    return s.get(url, stream=stream, verify=False)


def download(s, url, filepath):
    if os.path.exists(filepath):
        print(filepath)
        return
    print(f'\033[1;32m{filepath}\033[m')

    # TODO: progress bar
    tempfile = f'{filepath}.temp'
    r = get(s, url, stream=True)
    with open(tempfile, 'wb') as f:
        f.write(r.content)

    os.rename(tempfile, filepath)


def get_galleries(s, url):
    r = get(s, url)
    curr_page = page_regex.search(url)
    curr_page = 1 if not curr_page else int(curr_page.group(1))
    max_page = max(map(int, page_regex.findall(r.text)), default=1)
    galleries = list()
    for page in range(curr_page, max_page + 1):
        for link in gallery_regex.findall(r.text):
            gid, token = link.split('/')
            galleries.append([gid, token])

        if max_page > curr_page:
            if page_regex.search(url):
                url = re.sub(r'([\?\&]page)=(\d+)', r'\1={}'.format(page), url)
            else:
                url += f'&page={page}' if '?' in url else f'?page={page}'
            r = get(s, url)
    return galleries


def create_session():
    s = requests.Session()

    # https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
    retry = Retry(total=5, connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('http://', adapter)
    s.mount('https://', adapter)

    s.headers.update({'user-agent': UA})
    cj = MozillaCookieJar(COOKIE_FILE)
    cj.load(ignore_discard=True, ignore_expires=True)
    s.cookies = cj
    return s


def parse_gallery_info(html):
    if (title := title_regex.search(html)):
        title = title.group(1)
    elif (title := title_regex_fallback.search(html)):
        title = ''.join(title.group(1).split('-')[:-1])

    title = clean_filename(unescape(title))

    if (artist := artist_regex.search(html)):
        artist = artist.group(1)

    return title, artist


def download_gallery(s, url):
    if re.search(r'\.org/g/\d+', url):
        gid, token = re.search(r'/g/(\d+)/([^/]*)', url).group(1, 2)
        galleries = [(gid, token)]
    else:
        galleries = get_galleries(s, url)

    c, total = 1, len(galleries)
    for gid, token in galleries:
        url = f'https://e-hentai.org/g/{gid}/{token}/'
        r = get(s, url)
        title, artist = parse_gallery_info(r.text)

        if skip_regex and skip_regex.search(title):
            print(f'skipping: {title}')
            continue

        try:
            dl_dir = os.path.join(DL_DIR, f'{artist}/{title}')
        except AttributeError:
            dl_dir = os.path.join(DL_DIR, title)
        mkdir(dl_dir)

        print(f'gallery {c} of {total}: {title}, {url}')
        c += 1

        url = re.search(r'https://e-hentai\.org/s/[^/]*/\d*-1', r.text).group()
        curr_page = 0
        next_page = curr_page + 1
        while next_page > curr_page:
            att = 0
            while (att := att + 1) <= MAX_ATTEMPS:
                r = get(s, url)
                try:
                    img = img_regex.search(r.text).group(1)
                except AttributeError:
                    print(f'image not found, {url}, attempt: {att} of {MAX_ATTEMPS}')  # noqa: E501
                    continue

                if '/509.gif' in img:
                    print(f'509 IMAGE, {url} - {img}')
                    exit(1)

                filename = img.split('/')[-1].split('?')[0]
                filename, ext = os.path.splitext(filename)
                filename = '{}_page-{}{}'.format(filename, curr_page + 1, ext)
                filepath = os.path.join(dl_dir, filename)
                try:
                    download(s, img, filepath)
                    break
                except Exception:
                    print(f'download failed, {url}, attempt: {att} of {MAX_ATTEMPS}')  # noqa: E501

            curr_page = int(url.split('-')[-1])
            url = next_regex.search(r.text).group(1)
            next_page = int(url.split('-')[-1])


def main(urls):
    s = create_session()
    for url in urls:
        open(HISTORY, 'a').write(f'{url}\n')
        download_gallery(s, url)


if __name__ == '__main__':
    opts, args = parse_arguments()

    # TODO: change this
    if opts.cookie_file:
        copy(opts.cookie_file, COOKIE_FILE)
    if not os.path.exists(COOKIE_FILE):
        raise FileNotFoundError(COOKIE_FILE)

    if opts.input_file:
        with open(opts.input_file, 'r') as f:
            args = f.readlines()
    args = [i for i in args if 'e-hentai' in i]

    try:
        main(args)
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print(f'finished with errors, {err}')
