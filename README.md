# A basic launcher for kodi

Practically every launcher I've tested is broken, and needs too much work to fix, so I've written this very basic launcher.

Example games.json
```json
[
	{
		"id": "106455",
    "title": "Super Mario Galaxy",
    "description": "",
    "icon": "/home/games/thumb/Super Mario Galaxy.jpg",
    "fanart": "/home/games/fanart/Super Mario Galaxy.jpg",
    "poster": "/home/games/thumb/Super Mario Galaxy.jpg",
    "platform": "Wii",
    "genres": ["Action", "Adventure", "Platform"],
    "file": "/home/games/iso/Super Mario Galaxy.iso",
    "launch_command": "~/bin/dolphin-emu-nogui \"{file}\""
	}
]
```

Using the command line to populate a games.json automatically.

```bash
cd /path/to/mygames/
python3 ~/.kodi/addons/plugin.program.basiclauncher/generate_games_json.py
```

It's not 100% stable yet, but the tool will collect metadata from TheGamesDB.net if available. Using a folder structure you can provide
hints e.g. gamecube titles in a gamecube folder, so that the platform
will be correctly selected by the search.

TheGamesDB has quite a weak search algorithm, so filenames may not
generate good results. This is entirely up to you to fix, YMMV.

emu-wrapper script is included which you link to your home/bin folder
using the name of the binary you wish to launch.

```bash
ln -s emu-wrapper ~/bin/dolphin-emu-nogui
```

The emu-wrapper is very likely not going to work for you, unless you happen to have the same wireless remote as me. You'll need to edit the
script, and use evtest to identify the input you want to use to exit
the emulator.

First, get the evtest event, the user who is running the script will
need to be in the input group and the plugdev group.

```bash
groupadd input $USER
groupadd plugdev $USER
```

```bash
ls /dev/input/by-id/


evtest /dev/input/by-id/mydevice
# When evtest is running press the button you want to use
# for the exit event.
```


Edit the top two lines, device and exit_event to reflect your captured
values. 
```bash
device='/dev/input/by-id/usb-4037_2.4G_Composite_Devic-event-if01'
event_exit='*code 158 (KEY_BACK), value 0*'
```
