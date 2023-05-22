import json
import requests
import time
from copy import copy
from .Downloader import Downloader
import os
import re
from collections import Counter

regions = {

}

countries = {

}

aspect_ratios = {
    str(round(16.0 / 9.0 * 10)): "fanart",
    str(round(500.0 / 710.0 * 10)): "poster",
    str(round(500.0 / 700.0 * 10)): "poster",
    "10": "thumbnail"
}

platform_hints = [
    'ps1',
    'ps2',
    'wii',
    'gamecube',
    'xbox',
    'gamecube',
    'psp',
    'sega32x',
    'snes',
    'nes',
    'gameboy',
    'gameboycolor',
    '3ds',
    'gamegear',
    'gameboyadvance',
    'n64',
    'ds',
    'mastersystem',
    'megadrive'
]

platform_hint_re = '|'.join(platform_hints)
platform_hint_re = '('+platform_hint_re+')'

class TheGamesDB:
    def __init__(self, apikey, region=1, country=0):
        self.__base_url = "https://api.thegamesdb.net/v1/"
        self.region = region
        self.country = country
        self.downloader = Downloader("https://api.thegamesdb.net/v1/", 3000)
        self.downloader.start()
        self.cdndownloader = Downloader("https://cdn.thegamesdb.net/")
        self.cdndownloader.start()
        self.params = {
            "apikey": apikey
        }

        self.remaining_monthly_allowance = 0
        self.allowance_refresh_timer = 0
        self.bootstrap()
        self.load()

    def bootstrap(self):
        self.bootstrap_genres()
        self.bootstrap_platforms()
        self.bootstrap_studios()

    def load(self):
        localpath = os.path.dirname(os.path.abspath(__file__))
        genres = os.path.join(localpath, 'TheGamesDB/static/v1/Genres/index.json')
        platforms = os.path.join(localpath, 'TheGamesDB/static/v1/Platforms/index.json')
        studios = os.path.join(localpath, 'TheGamesDB/static/v1/Developers/index.json')
        with open(genres) as f:
            self.genres = json.loads(f.read())
        with open(platforms) as f:
            self.platforms = json.loads(f.read())
        with open(studios) as f:
            self.studios = json.loads(f.read())

        self.platform_name_lookup = {
            v['alias']: k
            for k, v in self.platforms['data']['platforms'].items()
        }


    def bootstrap_genres(self):
        localpath = os.path.dirname(os.path.abspath(__file__))
        localpath = os.path.join(localpath, 'TheGamesDB/static/v1/Genres/index.json')
        if not os.path.exists(localpath):
            print("Getting genre bootstrap")
            os.makedirs(os.path.dirname(localpath), exist_ok=True)
            data = self.downloader.add_item(
                "Genres",
                params=self.params,
                asynchronous=False
            )
            with open(localpath, 'wt') as f:
                f.write(json.dumps(data, indent=4, sort_keys=True))
            self.downloader.limit_expires = time.time() + data['allowance_refresh_timer']
            self.downloader.limit_size = data['remaining_monthly_allowance']

    def bootstrap_platforms(self):
        localpath = os.path.dirname(os.path.abspath(__file__))
        localpath = os.path.join(localpath, 'TheGamesDB/static/v1/Platforms/index.json')
        if not os.path.exists(localpath):
            print("Getting platforms bootstrap")
            os.makedirs(os.path.dirname(localpath), exist_ok=True)
            data = self.downloader.add_item(
                "Platforms",
                params=self.params,
                asynchronous=False
            )
            with open(localpath, 'wt') as f:
                f.write(json.dumps(data, indent=4, sort_keys=True))
            self.downloader.limit_expires = time.time() + data['allowance_refresh_timer']
            self.downloader.limit_size = data['remaining_monthly_allowance']

            params = copy(self.params)
            params['platforms_id'] = ','.join(data['data']['platforms'].keys())
            self.downloader.add_item(
                "Platforms/Images",
                params=params,
                callback=self.collect_images,
                userdata={}
            )

    def bootstrap_studios(self):
        localpath = os.path.dirname(os.path.abspath(__file__))
        localpath = os.path.join(localpath, 'TheGamesDB/static/v1/Developers/index.json')
        if not os.path.exists(localpath):
            print("Getting studios bootstrap")
            os.makedirs(os.path.dirname(localpath), exist_ok=True)
            data = self.downloader.add_item(
                "Developers",
                params=self.params,
                asynchronous=False
            )
            with open(localpath, 'wt') as f:
                f.write(json.dumps(data, indent=4, sort_keys=True))
            self.downloader.limit_expires = time.time() + data['allowance_refresh_timer']
            self.downloader.limit_size = data['remaining_monthly_allowance']


    def collect_images(self, data, userdata):
        path = data['data']['base_url']['original'][len(self.cdndownloader.base_url):]
        for k in data['data']['images'].keys():
            for image in data['data']['images'][k]:
                self.cdndownloader.add_item(
                    path + image['filename'],
                    callback=self.collect_image,
                    userdata={
                        "id": image['id'],
                        "platform_id": k,
                        "type": image['type'],
                        "filename": image['filename']
                    })

    def collect_image(self, data, userdata):
        """Write the image to disk and associate it to platform_id."""
        # platform = Platform.get(userdata['platform_id'])
        image_type = userdata['type']
        # image = Image.frombytes(data)
        # width, height = image.size
        extension = os.path.splitext(userdata['filename'])[1][1:]

        os.makedirs("cache", exist_ok=True)
        filename = "cache/platform-%s-%s-%s.%s" % (
            str(userdata['platform_id']),
            image_type,
            str(userdata['id']),
            extension
        )
        with open(filename, 'wb') as f:
            f.write(data)

    def close(self):
        self.downloader.close()
        self.cdndownloader.close()

    def get_platform_name(self, platform_id):
        try:
            return self.platforms['data']['platforms'][str(platform_id)]['name']
        except:
            return self.get_platform_name(self.get_platform_id(platform_id))


    def get_platform_id(self, platform_name):
        if platform_name is None:
            return None
        if platform_name in self.platform_name_lookup.keys():
            return self.platform_name_lookup[platform_name]
        return None

    def get_genre_names(self, genres):
        return [self.genres['data']['genres'][str(x)]['name'] for x in genres]

    def hints(self, name_string):
        years = re.findall(r'\d{4}', name_string)
        years = [int(y) for y in years if int(y) > 1960]
        platforms = re.findall(platform_hint_re, name_string.lower())
        # TODO: Region hints from PAL/NTSC
        #
        return years, platforms

    def clean_name(self, name_string):
        n = re.sub(r'\([^)]*\)', '', name_string)
        n = re.sub(r'-', ' ', n)
        n = re.sub(r'\.', ' ', n)
        n = re.sub(r'\[[^)]*\]', '', n)
        n = re.sub(r'[^A-Za-z0-9 ]+', '', n)
        return n

    def search(self, query_string, platform_id=None):
        if len(query_string) == 0:
            print("Error search is empty")
            return None
        # Return's prepared game object's for display
        name = self.clean_name(query_string)
        if len(name) == 0:
            print("Error search is empty")
            return None
        years, platforms = self.hints(query_string)
        print("Searching for %s" % name)
        path = "Games/ByGameName"
        params = copy(self.params)
        params = {
            "name": name,
            "fields": "players,publishers,genres,overview,last_updated,rating,platform"
        }

        if platform_id is not None:
            params.update({
                "include": "platform",
                "filter[platform]": platform_id
            })
        r = requests.get(self.__base_url + path, params=params)
        data = r.json()
        # self.downloader.limit_expires = time.time() + data['allowance_refresh_timer']
        self.downloader.limit_size = data['remaining_monthly_allowance']

        scores = Counter()
        index = {}
        words = set(name.split(' '))
        for game in data['data']['games']:
            index[str(game['id'])] = game
            score = 0
            t = game['game_title'].lower()
            c = self.clean_name(t)
            w = set(c.split(' '))

            if name == t:
                score += 1
            if name == w:
                score += 1
            if len(w.difference(words)) == 0:
                # All words that are in t, exist in the name
                score += 1
            if len(words.difference(w)) > 1:
                # More than one word difference between name and t
                score -= 1

            if len(name) > len(t):
                # If our title name is longer, it might be a sequel
                # penalise this name
                score -= 1

            if int(game['country_id']) == int(self.country):
                score += 1

            if int(game['region_id']) == int(self.region):
                score += 1

            for y in years:
                if game['release_date'].startswith(str(y)):
                    score += 1

            scores[str(game['id'])] = score

        game = scores.most_common()
        game['images'] = {}

        os.makedirs("cache", exist_ok=True)
        path = data['include']['boxart']['base_url']['original'][len(self.cdndownloader.base_url):]
        for image in data['include']['data'][str(game['id'])]:
            if image['side'] != 'front':
                continue

            localpath = os.path.dirname(os.path.abspath(__file__))
            local_image_file = "cache/game-%s-%s-%s.jpg" % (
                image['type'],
                str(game['id']),
                str(image['id'])
            )
            local_image_file = os.path.join(localpath, local_image_file)
            if os.path.exists(local_image_file):
                continue

            aspect = eval(image['resolution'].replace('x', ' / '))
            aspect = round(aspect * 10)
            if str(aspect) in aspect_ratios.keys():
                game['images'][aspect_ratios[str(aspect)]] = local_image_file
            else:
                continue
            self.cdndownloader.add_item(
                path + image['filename'],
                callback=self.collect_box_art,
                userdata={
                    "filename": local_image_file
                })

        return game

    def collect_box_art(self, data, userdata):
        with open(userdata['filename'], 'wb') as f:
            f.write(data)

if __name__ == '__main__':
    tgdb = TheGamesDB("968355110a135284d076b25991a49d1ea3c5797b54bbb5374a3ab0508fe05194")
