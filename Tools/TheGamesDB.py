import json
import requests
import time
from copy import copy
from .Downloader import Downloader
import os

regions = {

}

countries = {

}


class TheGamesDB:
    def __init__(self, apikey, region=1, country=0):
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

    def bootstrap_genres(self):
        localpath = os.path.dirname(os.path.abspath(__file__))
        localpath = os.path.join(localpath, 'TheGamesDB/static/v1/Genres/index.json')
        if not os.path.exists(localpath):
            print ("Getting genre bootstrap")
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
            print ("Getting platforms bootstrap")
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
            print ("Getting studios bootstrap")
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
        print (json.dumps(data, indent=4, sort_keys=True))
        path = data['data']['base_url']['original'][len(self.cdndownloader.base_url):]
        for k in data['data']['images'].keys():
            for image in data['data']['images'][k]:
                print (path + image['filename'])
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

    def clean_name(self, name_string):
        # Strip anything between brackets
        # strip punctuation
        
        return name_string

    def search(self, query_string, platform_id=None):
        # Return's prepared game object's for display
        path = "/v1/Games/ByGameName"
        params = copy(self.params)
        params = {
            "name": self.clean_name(query_string),
            "fields": "players,publishers,genres,overview,last_updated,rating,platform"
        }

        if platform_id is not None:
            params.update({
                "include": "platform",
                "filter[platform]": platform_id
            })
        r = requests.get(self.__base_url + path, params=params)
        data = r.json()
        self.downloader.limit_expires = time.time() + data['allowance_refresh_timer']
        self.downloader.limit_size = data['remaining_monthly_allowance']

        return data['data']



if __name__ == '__main__':
    tgdb = TheGamesDB("968355110a135284d076b25991a49d1ea3c5797b54bbb5374a3ab0508fe05194")
