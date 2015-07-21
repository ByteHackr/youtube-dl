from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_urllib_request
from ..utils import (
    float_or_none,
    unescapeHTML,
)


class TwitterCardIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?twitter\.com/i/cards/tfw/v1/(?P<id>\d+)'
    _TEST = {
        'url': 'https://twitter.com/i/cards/tfw/v1/560070183650213889',
        'md5': 'a74f50b310c83170319ba16de6955192',
        'info_dict': {
            'id': '560070183650213889',
            'ext': 'mp4',
            'title': 'TwitterCard',
            'thumbnail': 're:^https?://.*\.jpg$',
            'duration': 30.033,
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        # Different formats served for different User-Agents
        USER_AGENTS = [
            'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/20.0 (Chrome)',  # mp4
            'Mozilla/5.0 (Windows NT 5.2; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',  # webm
        ]

        config = None
        formats = []
        for user_agent in USER_AGENTS:
            request = compat_urllib_request.Request(url)
            request.add_header('User-Agent', user_agent)
            webpage = self._download_webpage(request, video_id)

            config = self._parse_json(
                unescapeHTML(self._search_regex(
                    r'data-player-config="([^"]+)"', webpage, 'data player config')),
                video_id)

            video_url = config['playlist'][0]['source']

            f = {
                'url': video_url,
            }

            m = re.search(r'/(?P<width>\d+)x(?P<height>\d+)/', video_url)
            if m:
                f.update({
                    'width': int(m.group('width')),
                    'height': int(m.group('height')),
                })
            formats.append(f)
        self._sort_formats(formats)

        thumbnail = config.get('posterImageUrl')
        duration = float_or_none(config.get('duration'))

        return {
            'id': video_id,
            'title': 'TwitterCard',
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': formats,
        }


class TwitterIE(TwitterCardIE):
    _VALID_URL = r'https?://(?:www|m|mobile)?\.?twitter\.com/(?P<id>[^/]+/status/\d+)'

    _TESTS = [{
        'url': 'https://m.twitter.com/thereaIbanksy/status/614301758345490432',
        'md5': '8bbccb487bd7a31349b775915fcd412f',
        'info_dict': {
            'id': '614301758345490432',
            'ext': 'mp4',
            'title': 'thereaIbanksy - This time lapse is so pretty \U0001f60d\U0001f60d',
            'thumbnail': 're:^https?://.*\.jpg',
            'duration': 29.5,
            'description': 'banksy on Twitter: "This time lapse is so pretty \U0001f60d\U0001f60d http://t.co/QB8DDbqiR1"',
            'uploader': 'banksy',
            'uploader_id': 'thereaIbanksy',
        },
    }]

    def _real_extract(self, url):
        id = self._match_id(url)
        username, twid = re.match(r'([^/]+)/status/(\d+)', id).groups()
        name = username
        url = re.sub(r'https?://(m|mobile)\.', 'https://', url)
        webpage = self._download_webpage(url, 'tweet: ' + url)
        description = unescapeHTML(self._search_regex('<title>\s*(.+?)\s*</title>', webpage, 'title'))
        title = description.replace('\n', ' ')
        splitdesc = re.match(r'^(.+?)\s*on Twitter:\s* "(.+?)"$', title)
        if splitdesc:
            name, title = splitdesc.groups()
        title = re.sub(r'\s*https?://[^ ]+', '', title)  # strip  'https -_t.co_BJYgOjSeGA' junk from filenames
        card_id = self._search_regex(r'["\']/i/cards/tfw/v1/(\d+)', webpage, '/i/card/...')
        card_url = 'https://twitter.com/i/cards/tfw/v1/' + card_id
        return {
            '_type': 'url_transparent',
            'ie_key': 'TwitterCard',
            'uploader_id': username,
            'uploader': name,
            'url': card_url,
            'webpage_url': url,
            'description': description,
            'title': username + ' - ' + title,
        }
