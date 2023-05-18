# A basic launcher for kodi 

Practically every launcher I've tested is broken, and needs too much work to fix, so I've written this very basic launcher. 

I have other tools for generating the necessary games.json file but they're currently incomplete. This is just a stop gap.

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

emu-wrapper script is included which you link to your emulator binary. 

```bash
ln -s emu-wrapper ~/bin/dolphin-emu-nogui
```


