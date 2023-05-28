import os
import sys
import urllib
import urllib.parse as urlparse
# http://mirrors.kodi.tv/docs/python-docs/
import xbmcaddon
import xbmcgui
import xbmc
import xbmcplugin
import json
import csv
from collections import defaultdict
from subprocess import run

xbmc.log("Loading plugin basic launcher", xbmc.LOGERROR)

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urlparse.urlencode(query)


def make_game_item(game):
    li = xbmcgui.ListItem(label=game['title'])
    li.setArt({
        'poster': game.get('poster'),
        'icon': game.get('icon'),
        'fanart': game.get('fanart')
        # 'thumb' : game.get('Screenshot')
    })
    # set the list item to playable
    li.setProperty('IsPlayable', 'true')
    li.setProperty('description', game.get('description'))
    li.setInfo('video', {'title': game['title'], 'plot': game.get('description')})
    # build the plugin url for Kodi
    url = build_url({'mode': 'stream', 'url': game['id'], 'title': game['title']})
    xbmc.log(url, level=xbmc.LOGERROR)
    return (url, li, True)

def make_folder_item(folder):
    li = xbmcgui.ListItem(label=folder['name'])
    li.setArt({
    })
    li.setProperty('IsPlayable', 'false')
    li.setInfo('video', {'title': folder['name']})
    url = build_url({'mode': 'folder', 'url': folder['path'], 'title': folder['name']})
    xbmc.log(url, level=xbmc.LOGERROR)
    return (url, li, True)


def build_tree(games):
    index = {}
    genres = defaultdict(list)
    platforms = defaultdict(list)
    for game in games:
        index[str(game['id'])] = game
        for genre in game.get('genres', []):
            genres[genre].append(game['id'])
        platforms[game.get('platform', 'Unknown')].append(game['id'])


    return index, {
        'Genres': genres,
        'Platforms': platforms
    }


p = os.path.abspath(__file__)
p = os.path.dirname(p)
games_file = os.path.join(p, 'games.json')
with open(games_file) as f:
    games = json.loads(f.read())

index, tree = build_tree(games)
xbmc.log(str(tree), level=xbmc.LOGERROR)


def build_menu(args):
    menu_items = []
    if args.get('mode', None) is None:
        xbmc.log("Root menu", level=xbmc.LOGERROR)
        for k in tree.keys():
            item = make_folder_item({
                'path': k,
                'name': k,
                'icon': None,
                'poster': None,
                'fanart': None
            })
            menu_items.append(item)
    elif args.get('url', None) is not None:
        xbmc.log("Path %s" % str(args.get('url')), level=xbmc.LOGERROR)
        items = tree
        path = args.get('url').split('/')
        for p in path:
            items = items[p]
        xbmc.log(str(items), level=xbmc.LOGERROR)

        if type(items) == defaultdict:
            for k in items.keys():
                xbmc.log("Errorlog %s" % k, level=xbmc.LOGERROR)
                item = make_folder_item({
                    'path': args.get('url') + '/' + k,
                    'name': k,
                    'icon': None,
                    'poster': None,
                    'fanart': None
                })
                menu_items.append(item)
        else:
            xbmc.log("Errorlog %s" % str(items), level=xbmc.LOGERROR)
            for key in items:
                item = index[str(key)]
                menu_items.append(make_game_item(item))

    xbmcplugin.addDirectoryItems(addon_handle, menu_items, len(menu_items))
    xbmcplugin.setContent(addon_handle, 'movies')
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    xbmc.executebuiltin('Container.SetViewMode(%d)' % 65536)


def play_game(game_id):
    xbmc.log("Starting item: %s" % str(game_id), level=xbmc.LOGERROR)
    game = index[game_id]
    cmd = game['launch_command'].format(**game)
    xbmc.log("Executing: %s" % cmd, level=xbmc.LOGERROR)
    os.system(game['launch_command'].format(**game))


def main():
    xbmc.log("Starting basic launcher plugin", level=xbmc.LOGERROR)
    args = urlparse.parse_qs(sys.argv[2][1:])
    args = {k:v[0] for k, v in args.items()}
    xbmc.log("args: %s" % str(args), level=xbmc.LOGERROR)
    mode = args.get('mode', None)

    if mode is not None and mode == 'stream':
        play_game(args['url'])
        return

    build_menu(args)

if __name__ == '__main__':

    addon_handle = int(sys.argv[1])
    xbmc.log(str(addon_handle), level=xbmc.LOGERROR)
    main()
