import json
import sys
import os
import uuid
from pathlib import Path
from Tools.TheGamesDB import TheGamesDB

tgdb_api_key = "968355110a135284d076b25991a49d1ea3c5797b54bbb5374a3ab0508fe05194"
tgdb = TheGamesDB(tgdb_api_key)

try:
    with open("~/.kodi/addons/plugin.program.basiclauncher/games.json") as f:
        games = json.loads(f.read())
except:
    games = []

found_files = [x['file'] for x in games]


extensions_platforms = {
    "iso": ["ps1", "ps2", "wii", "gamecube", "xbox"],
    "gcm": ["gamecube"],
    "cso": ["psp"],
    "32x": ["sega32x"],
    "smc": ["snes"],
    "nes": ["nes"],
    "gb": ["gameboy"],
    "gbc": ["gameboycolor"],
    "3ds": ["3ds"],
    "gg": ["gamegear"],
    "gba": ["gameboyadvance"],
    "n64": ["n64"],
    "z64": ["n64"],
    "nds": ["ds"],
    "sms": ["mastersystem"],
    "gen": ["megadrive"]
}

platform_launch_commands = {
    "ps2": "~/bin/PCSX2 --fullscreen --nogui",
    "wii": "~/bin/dolphin-emu-nogui",
    "psp": "~/bin/PPSSPPSDL --fullscreen",
    "gamecube": "~/bin/dolphin-emu-nogui"
}

platform_match = {
    "3do": "3do",
    "acorn-archimedes": "acorn-archimedes",
    "acorn-atom": "acorn-atom",
    "acorn-electron": "acorn-electron",
    "action-max": "action-max",
    "amiga": "amiga",
    "amiga-cd32": "amiga-cd32",
    "amstrad-cpc": "amstrad-cpc",
    "amstrad-gx4000": "amstrad-gx4000",
    "android": "android",
    "apf-mp-1000": "apf-mp-1000",
    "apple-pippin": "apple-pippin",
    "apple2": "apple2",
    "arcade": "arcade",
    "atari-2600": "atari-2600",
    "atari-5200": "atari-5200",
    "atari-7800": "atari-7800",
    "atari-jaguar": "atari-jaguar",
    "atari-jaguar-cd": "atari-jaguar-cd",
    "atari-lynx": "atari-lynx",
    "atari-st": "atari-st",
    "atari-xe": "atari-xe",
    "atari800": "atari800",
    "bally-astrocade": "bally-astrocade",
    "bandai-tv-jack-5000": "bandai-tv-jack-5000",
    "bbc-bridge-companion": "bbc-bridge-companion",
    "bbc-micro": "bbc-micro",
    "c128": "c128",
    "casio-loopy": "casio-loopy",
    "casio-pv-1000": "casio-pv-1000",
    "coleco-telstar-arcade": "coleco-telstar-arcade",
    "colecovision": "colecovision",
    "commodore-16": "commodore-16",
    "commodore-64": "commodore-64",
    "commodore-pet": "commodore-pet",
    "commodore-plus/4": "commodore-plus/4",
    "commodore-vic20": "commodore-vic20",
    "didj": "didj",
    "dragon32-64": "dragon32-64",
    "emerson-arcadia-2001": "emerson-arcadia-2001",
    "entex-adventure-vision": "entex-adventure-vision",
    "entex-select-a-game": "entex-select-a-game",
    "epoch-cassette-vision": "epoch-cassette-vision",
    "epoch-super-cassette-vision": "epoch-super-cassette-vision",
    "evercade": "evercade",
    "fairchild": "fairchild",
    "fds": "fds",
    "fmtowns": "fmtowns",
    "fujitsu-fm-7": "fujitsu-fm-7",
    "gakken-compact-vision": "gakken-compact-vision",
    "gamate": "gamate",
    "game-and-watch": "game-and-watch",
    "game-com": "game-com",
    "game-wave": "game-wave",
    "gizmondo": "gizmondo",
    "gp32": "gp32",
    "hyperscan": "hyperscan",
    "intellivision": "intellivision",
    "interton-vc-4000": "interton-vc-4000",
    "ios": "ios",
    "j2me-(java-platform,-micro-edition)": "j2me-(java-platform,-micro-edition)",
    "lcd": "lcd",
    "mac-os": "mac-os",
    "magnavox-odyssey": "magnavox-odyssey",
    "magnavox-odyssey-2": "magnavox-odyssey-2",
    "mattel-aquarius": "mattel-aquarius",
    "megaduck": "megaduck",
    "microsoft-xbox": "microsoft-xbox",
    "microsoft-xbox-360": "microsoft-xbox-360",
    "microsoft-xbox-one": "microsoft-xbox-one",
    "microsoft-xbox-series-x": "microsoft-xbox-series-x",
    "milton-bradley-microvision": "milton-bradley-microvision",
    "msx": "msx",
    "neo-geo-cd": "neo-geo-cd",
    "neo-geo-pocket": "neo-geo-pocket",
    "neo-geo-pocket-color": "neo-geo-pocket-color",
    "neogeo": "neogeo",
    "ngage": "ngage",
    "3ds": "nintendo-3ds",
    "n64": "nintendo-64",
    "ds": "nintendo-ds",
    "nes": "nintendo-entertainment-system-nes",
    "gameboy": "nintendo-gameboy",
    "gameboyadvance": "nintendo-gameboy-advance",
    "gameboycolor": "nintendo-gameboy-color",
    "gamecube": "nintendo-gamecube",
    "nintendo-pokmon-mini": "nintendo-pokmon-mini",
    "switch": "nintendo-switch",
    "virtualboy": "nintendo-virtual-boy",
    "wii": "nintendo-wii",
    "wiiu": "nintendo-wii-u",
    "nuon": "nuon",
    "oculus-quest": "oculus-quest",
    "oric-1": "oric-1",
    "ouya": "ouya",
    "palmtex-super-micro": "palmtex-super-micro",
    "pc": "pc",
    "pc88": "pc88",
    "pc98": "pc98",
    "pcfx": "pcfx",
    "philips-cd-i": "philips-cd-i",
    "philips-tele-spiel-es-2201": "philips-tele-spiel-es-2201",
    "playdate": "playdate",
    "playdia": "playdia",
    "r-zone": "r-zone",
    "rca-studio-ii": "rca-studio-ii",
    "sam-coupe": "sam-coupe",
    "sega32x": "sega-32x",
    "segacd": "sega-cd",
    "dreamcast": "sega-dreamcast",
    "gamegear": "sega-game-gear",
    "genesis": "sega-genesis",
    "mastersystem": "sega-master-system",
    "megadrive": "sega-mega-drive",
    "sega-pico": "sega-pico",
    "saturn": "sega-saturn",
    "sg1000": "sg1000",
    "sharp-x1": "sharp-x1",
    "shg-black-point": "shg-black-point",
    "sinclair-zx-spectrum": "sinclair-zx-spectrum",
    "sinclair-zx80": "sinclair-zx80",
    "sinclair-zx81": "sinclair-zx81",
    "ps1": "sony-playstation",
    "ps2": "sony-playstation-2",
    "ps3": "sony-playstation-3",
    "ps4": "sony-playstation-4",
    "ps5": "sony-playstation-5",
    "psvita": "sony-playstation-vita",
    "psp": "sony-psp",
    "stadia": "stadia",
    "snes": "super-nintendo-snes",
    "tandy-vis": "tandy-vis",
    "tapwave-zodiac": "tapwave-zodiac",
    "texas-instruments-ti-99-4a": "texas-instruments-ti-99-4a",
    "tomy-pyta": "tomy-pyta",
    "trs80-color": "trs80-color",
    "turbo-grafx-cd": "turbo-grafx-cd",
    "turbografx-16": "turbografx-16",
    "v-smile": "v-smile",
    "vectrex": "vectrex",
    "vtech-creativision": "vtech-creativision",
    "vtech-socrates": "vtech-socrates",
    "watara-supervision": "watara-supervision",
    "wonderswan": "wonderswan",
    "wonderswan-color": "wonderswan-color",
    "x68": "x68",
    "xavix-port": "xavix-port"
}

all_platforms = [e for nested in extensions_platforms.values() for e in nested]


def guess_platform(filename):
    """
    Try to guess the game platform from the folder or file extension.
    """
    dir = os.path.dirname(filename)
    fn = os.path.basename(filename)
    lc = fn.lower()
    (name, ext) = os.path.splitext(lc)
    ext = ext[1:]

    guesses = []
    if ext in extensions_platforms.keys():
        guesses.extend(extensions_platforms[ext])

    hinted = []
    paths = dir.lower().split('/')
    for p in paths:
        if p in all_platforms:
            hinted.append(p)

    if len(hinted) == 1:
        return hinted
    if len(guesses) == 1:
        return guesses[0]

    return "Unknown"


def create_game_entry(filename):
    platform = guess_platform(filename)
    dir = os.path.dirname(filename)
    fn = os.path.basename(filename)
    (name, ext) = os.path.splitext(fn)
    if platform not in platform_launch_commands.keys():
        print("Cannot locate the launch command for platform: %s" % platform)
        return None

    platform_id = tgdb.get_platform_id(platform_match.get(platform))
    platform_name = tgdb.get_platform_name(platform_id)
    result = tgdb.search(name.lower(), platform_id)
    cmd = platform_launch_commands[platform]

    game = {
        "id": result['id'],
        "title": result['game_title'],
        "description": result['overview'],
        "icon": os.path.join(dir, "Thumbnails/", name+".jpg"),
        "fanart": os.path.join(dir, "Fanart/", name+".jpg"),
        "poster": os.path.join(dir, "Thumbnails/", name+".jpg"),
        "platform": platform_name,
        "genres": tgdb.get_genre_names(result['genres']),
        "rating": result['rating'],
        "release_date": result['release_date'],
        "file": filename,
        "launch_command": cmd + " \"{file}\""
    }
    return game


def find_games(path):
    files = (p.resolve() for p in Path(path).glob("**/*") if p.suffix in {'.'+e for e in extensions_platforms.keys()})

    for f in files:
        if f in found_files:
            continue
        game = create_game_entry(f)
        if game is not None:
            games.append(game)

    # TODO: Scan moonlight if available


if __name__ == '__main__':
    find_games(os.getcwd())
    print("Games loaded")
    tgdb.close()
