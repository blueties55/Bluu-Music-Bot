import discord
from discord.ext import commands
import yt_dlp
import asyncio
import configparser
import logging

logger = logging.getLogger("bot")

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 30',
    'options': '-vn'
}

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.now_playing = {}
        self.load_settings()

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('settings.txt', encoding='utf-8')
        self.allowed_channel_id = int(config.get('DEFAULT', 'allowed_channel_id', fallback=0))
        self.command_prefix = config.get('SETTINGS', 'command_prefix', fallback='?')

    async def search_youtube(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'ytsearch',
            'noplaylist': False  # Allow playlists
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                songs = []

                if 'entries' in info:  # Playlist or search result
                    for entry in info['entries']:
                        if entry:
                            songs.append({
                                'title': entry.get('title', 'Unknown Title'),
                                'url': entry.get('url'),
                                'webpage_url': entry.get('webpage_url', ''),
                                'duration': entry.get('duration', 0),
                                'thumbnail': entry.get('thumbnail'),
                                'uploader': entry.get('uploader', 'Unknown')
                            })
                else:  # Single video
                    songs.append({
                        'title': info.get('title', 'Unknown Title'),
                        'url': info.get('url'),
                        'webpage_url': info.get('webpage_url', ''),
                        'duration': info.get('duration', 0),
                        'thumbnail': info.get('thumbnail'),
                        'uploader': info.get('uploader', 'Unknown')
                    })

                return songs

            except Exception as e:
                logger.error(f"YT-DLP error: {e}")
                return []  # Always return a list

    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        queue = self.song_queue.get(guild_id)
        if queue:
            next_song = queue.pop(0)
            await self.play_song(ctx, next_song)
        else:
            self.now_playing[guild_id] = None
            voice_client = ctx.guild.voice_client
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()

    async def play_song(self, ctx, song):
        guild_id = ctx.guild.id
        self.now_playing[guild_id] = song
        voice_client = ctx.guild.voice_client

        # Disconnect if connected to wrong channel
        if voice_client and voice_client.channel != ctx.author.voice.channel:
            await voice_client.disconnect()
            voice_client = None

        # Connect if needed
        if not voice_client or not voice_client.is_connected():
            try:
                voice_client = await ctx.author.voice.channel.connect()
            except Exception as e:
                logger.error(f"Failed to connect: {e}")
                await ctx.send("❌ Could not connect to the voice channel.")
                return

        # Prepare audio source
        try:
            source = await discord.FFmpegOpusAudio.from_probe(
                song['url'],
                before_options=FFMPEG_OPTIONS['before_options'],
                options=FFMPEG_OPTIONS['options']
            )
        except Exception as e:
            logger.error(f"FFmpeg failed: {e}")
            await ctx.send("❌ Failed to stream the song. It may be unavailable.")
            return

        def after_playing(error):
            if error:
                logger.error(f"Playback error: {error}")
            asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

        voice_client.play(source, after=after_playing)
        await ctx.send(f"🎶 Now playing: **{song['title']}** by *{song['uploader']}*")

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, search: str):
        """Add a song to queue. Search YouTube or use a URL."""
        if not ctx.author.voice:
            await ctx.send("❌ Join a voice channel first.")
            return
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send(f"❌ Use <#{self.allowed_channel_id}> for music commands.")
            return

        songs = await self.search_youtube(search)
        if not songs:
            await ctx.send("❌ Could not find any songs.")
            return

        guild_id = ctx.guild.id
        queue = self.song_queue.setdefault(guild_id, [])
        voice_client = ctx.guild.voice_client

        # Playlist
        if len(songs) > 1:
            queue.extend(songs)
            await ctx.send(f"📃 Added **{len(songs)} songs** to the queue.")
            if not (voice_client and voice_client.is_playing()):
                await self.play_song(ctx, queue.pop(0))

        # Single song
        else:
            song = songs[0]
            if voice_client and voice_client.is_playing():
                queue.append(song)
                await ctx.send(f"🎵 Added to queue: **{song['title']}** by *{song['uploader']}*")
            else:
                await self.play_song(ctx, song)

    @commands.command(aliases=["s"])
    async def stop(self, ctx):
        """Stops all playback, clears queue, and disconnects bot."""
        if not ctx.author.voice:
            await ctx.send("❌ Join a voice channel first.")
            return

        voice_client = ctx.guild.voice_client
        if voice_client:
            voice_client.stop()
            guild_id = ctx.guild.id
            self.song_queue[guild_id] = []
            self.now_playing[guild_id] = None
            await voice_client.disconnect()
            await ctx.send("⏹️ Stopped playing and cleared the queue.")
        else:
            await ctx.send("❌ Nothing is playing.")

    @commands.command(aliases=["sk"])
    async def skip(self, ctx):
        """Skips the song in the 'now playing' position."""
        if not ctx.author.voice:
            await ctx.send("❌ Join a voice channel first.")
            return

        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("⏭️ Skipping to next song...")
        else:
            await ctx.send("❌ Nothing is playing.")

    @commands.command(aliases=["np"])
    async def nowplaying(self, ctx):
        """Displays the song that is in the 'now playing' position."""
        if not ctx.author.voice:
            await ctx.send("❌ Join a voice channel first.")
            return

        song = self.now_playing.get(ctx.guild.id)
        if not song:
            await ctx.send("❌ No song is currently playing.")
            return

        embed = discord.Embed(
            title=song['title'],
            url=song['webpage_url'],
            description=f"🎤 **Artist:** {song['uploader']}\n⏱️ **Duration:** {song['duration']}s",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=song['thumbnail'])
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))