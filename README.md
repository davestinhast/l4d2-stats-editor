# L4D2 Stats Editor

A tool to read and edit your Left 4 Dead 2 Steam stats directly from a command line window. No GUI, no extra dependencies, just run the .exe and start editing.

## What it does

Opens a CMD window that connects to your Steam account, loads your current L4D2 stats, and lets you change any value before writing them back to Steam.

Stats are organized into categories:

- General / Campaign (infected killed, medkits, revives, playtime, etc.)
- Versus (games played, wins, losses, per-infected stats and damage records)
- Weapons - Pistols and SMGs (shots, kills, headshots per weapon)
- Weapons - Shotguns
- Weapons - Rifles and Snipers
- Weapons - Melee (kills per melee weapon)
- Survival and Scavenge modes

For each stat it shows the current value from your account. You type a new number and press Enter to queue it. When you are done, it writes all the queued changes to Steam at once.

## Requirements

- Steam must be open and logged in
- Left 4 Dead 2 must be closed while editing
- .NET Framework 4.x (already installed on most Windows systems)

## How to use

1. Download the `dist` folder
2. Open the `dist` folder, run `L4D2_Stats_Editor.exe`
3. A CMD window will open and connect to Steam
4. Pick a category number from the menu
5. The stats for that category appear with their current values
6. Press `s` to start editing, type a new number for any stat you want to change, or press Enter to skip
7. When done with all categories, press `A` to apply and press `s` to confirm

The changes go through directly to Steam. They should reflect in your profile within a few minutes.

## How it works

The editor uses two components:

**sam_bridge.exe** is a small C# program that talks to Steam using the same API as the [Steam Achievement Manager (SAM)](https://github.com/gibbed/SteamAchievementManager). It connects through `steamclient.dll`, which is already on your machine as part of Steam. It requests your stats using `RequestUserStats`, waits for the callback, then reads or writes values by name.

**L4D2_Stats_Editor.exe** is the interface. It launches sam_bridge as a subprocess, shows the stats in a table, collects your input, and sends the changes back through the bridge.

Stat names were pulled directly from the local Steam schema cache at `Steam/appcache/stats/UserGameStatsSchema_550.bin`.

## Building from source

Requirements: Python 3.x, .NET Framework 4.x, SAM.API.dll from [SAM releases](https://github.com/gibbed/SteamAchievementManager/releases)

Place `SAM.API.dll` in the project folder and run `build.bat`. It will compile `sam_bridge.exe` using the .NET Framework compiler, install Python dependencies, and produce `dist/L4D2_Stats_Editor.exe`.

## Notes

- This only edits stats, not achievements
- Stats that use the `.Total` suffix are the ones shown on your Steam profile
- Some stats are read-only on the profile side but can still be written (average and recent values)
- The tool does not bypass any Steam protections, it writes stats the same way the game itself does

## Credits

Uses [SAM.API.dll](https://github.com/gibbed/SteamAchievementManager) by gibbed for Steam client communication.
