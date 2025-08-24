# Bluu Music Bot

Bluu Music Bot is a Discord bot that allows users to play and manage music within voice channels. It supports features like song queueing, playback control, and role-based command access.

## Features

- 🎶 Play music from YouTube and other sources
- 🔁 Queue management with shuffle and remove options
- ⏹️ Playback control: play, skip, stop
- 🔐 Role-based command access for DJs
- 📩 Customizable direct message responses
- 📃 Playlist support (adds multiple songs to the queue at once)

## Prerequisites

Ensure you have the following installed:

- Python 3.10 or higher
- FFmpeg (for audio playback)
- pip (Python package installer)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/blueties55/Bluu-Music-Bot/bluu-music-bot.git
   ```
   ```bash
   cd bluu-music-bot
   ```
2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example configuration settings file:

    ```bash
    cp settings.example.txt settings.txt
    ```
4. Open `settings.txt` in a text editor and replace the placeholders with your actual values:

   - DISCORD_API_TOKEN: Your Discord bot token
   - allowed_channel_id: The ID of the text channel for music commands
   - dj_role_id: The ID or name of the DJ role
   - command_prefix: Prefix for bot commands (default is ?)
   - mentions_as_prefix: Whether @mentions can be used as a command prefix (True or False)
   - dm_response: Message sent when the bot receives a DM

   Important: Do not change the parameter names (everything before the = sign).

Usage
-----

Run the bot with:

   python3 main.py

The bot will log in and load all cogs. It will only respond to commands in the channel specified by allowed_channel_id.

Commands
--------

- ?play <song or playlist>: Play a song or an entire playlist
- ?skip: Skip the current song
- ?stop: Stop playback and clear the queue
- ?queue: Display the current song queue
- ?shuffle: Shuffle the queue
- ?remove <position>: Remove a song from the queue
- ?nowplaying: Show the currently playing song
- ?move <from> <to>: Move a song in the queue (DJ role required)

Note: Commands that modify the queue may require the DJ role.

Contributing
------------

Contributions are welcome! Fork the repository, make your changes, and submit a pull request.
Ensure your code follows the existing style and includes appropriate testing.

License
-------

Bluu Music Bot is open-source software licensed under the MIT License.
