import os
import re

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'  # noqa: E501
HOME = os.getenv('HOME')
CACHE_DIR = os.getenv('XDG_CACHE_HOME', os.path.join(HOME, '.cache'))
DL_DIR = os.getenv('XDG_DOWNLOAD_DIR', os.path.join(HOME, 'Downloads/e-hentai'))
COOKIE_FILE = os.path.join(CACHE_DIR, 'e-hentai.cookie')
HISTORY = os.path.join(CACHE_DIR, 'e-hentai_history')
MAX_ATTEMPS = 5

gallery_regex = re.compile(r'href=\"https://e-hentai\.org/g/(\d*/[^/]*)/')
page_regex = re.compile(r'[\?\&]page=(\d+)')
# img_regex = re.compile(r'https://\w*\.\w*\.hath\.network(?:\:\d+)?/\w/[^\"]*\.(?:jpe?g|png|gif)')  # noqa: E501
img_regex = re.compile(r'<img id=\"img\" src=\"([^\"]*)')
title_regex = re.compile(r'<h1 id="gn">([^<]*)</h1>')
title_regex_fallback = re.compile(r'<title>([^<]*)</title>')
next_regex = re.compile(r'<a id="next"[^>]*href=\"([^\"]*-\d+)\"')
artist_regex = re.compile(r'<a id="ta_artist:([^\"]*)')
skip_regex = re.compile(r'twitter|collection|gallery|hd pack', re.IGNORECASE)  # noqa: E501
skip_regex = None
