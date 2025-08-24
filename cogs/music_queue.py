import discord
from discord.ext import commands
import configparser
import logging
import random

logger = logging.getLogger("bot")

class QueueManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channel_id = ""
        self.allowed_role_id = ""
        self.load_settings()

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('settings.txt', encoding='utf-8')
        self.allowed_channel_id = int(config.get("DEFAULT", "allowed_channel_id"))
        self.allowed_role_id = config.get("DEFAULT", "dj_role_id")

    def get_player_cog(self):
        return self.bot.get_cog("MusicPlayer")

    async def is_allowed_channel(self, ctx):
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send(f"❌ Please use <#{self.allowed_channel_id}> for music commands.")
            return False
        return True
    
    async def is_allowed_role(self, ctx):
        if not any(role.name == self.allowed_role_id for role in ctx.author.roles):
            await ctx.send(f"❌ You don't have the required DJ 🎧 role. Buy this role from the <#1210322451926491146> channel.")
            return False
        return True

    @commands.command(name="queue", aliases=["q"])
    async def show_queue(self, ctx):
        """Displays the current music queue."""
        if not await self.is_allowed_channel(ctx):
            return

        player = self.get_player_cog()
        if not player:
            await ctx.send("❌ MusicPlayer cog is not loaded.")
            return

        guild_id = ctx.guild.id
        queue = player.song_queue.get(guild_id, [])
        now_playing = player.now_playing.get(guild_id)

        if not queue and not now_playing:
            await ctx.send("📭 The queue is empty.")
            return

        embed = discord.Embed(title="🎶 Music Queue", color=discord.Color.purple())

        if now_playing:
            embed.add_field(name="Now Playing", value=f"**{now_playing['title']}**", inline=False)

        if queue:
            limited_queue = queue[:25]
            queue_list = "\n".join(
                [f"`{idx + 1}.` {song['title']}" for idx, song in enumerate(limited_queue)]
            )
            embed.add_field(name="Up Next", value=queue_list[:1024], inline=False)

            # Indicate if there are more songs
            if len(queue) > 25:
                embed.set_footer(text=f"...and {len(queue) - 25} more songs in the queue.")


        await ctx.send(embed=embed)

    @commands.command(name="clear", aliases=["clearqueue"])
    async def clear_queue(self, ctx):
        """Clears the queue but keeps the current song playing and stays connected."""
        if not await self.is_allowed_channel(ctx):
            return

        player = self.get_player_cog()
        if not player:
            await ctx.send("❌ MusicPlayer cog is not loaded.")
            return

        guild_id = ctx.guild.id
        player.song_queue[guild_id] = []
        await ctx.send("🧹 Cleared the queue. Now playing will continue.")

    @commands.command(aliases=["r"])
    async def remove(self, ctx, index: int):
        """Removes a specific song from the queue by its position number."""
        if not await self.is_allowed_channel(ctx):
            return

        player = self.get_player_cog()
        if not player:
            await ctx.send("❌ MusicPlayer cog is not loaded.")
            return

        guild_id = ctx.guild.id
        queue = player.song_queue.get(guild_id)

        if not queue:
            await ctx.send("📭 The queue is currently empty.")
            return

        if index < 1 or index > len(queue):
            await ctx.send(f"❌ Invalid index. Please use a number between 1 and {len(queue)}.")
            return

        removed_song = queue.pop(index - 1)
        await ctx.send(f"🗑️ Removed **{removed_song['title']}** from the queue.")

    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Please provide a **valid number** for the queue position.")

    @commands.command(aliases=["sh"])
    async def shuffle(self, ctx):
        """Shuffles the current queue."""
        if not await self.is_allowed_channel(ctx):
            return

        player = self.get_player_cog()
        if not player:
            await ctx.send("❌ MusicPlayer cog is not loaded.")
            return

        guild_id = ctx.guild.id
        queue = player.song_queue.get(guild_id)

        if not queue:
            await ctx.send("📭 There's nothing in the queue to shuffle.")
            return

        random.shuffle(queue)
        await ctx.send("🔀 Queue shuffled!")

    @commands.command(aliases=["m"])
    async def move(self, ctx, from_pos: int, to_pos: int = 1):
        """Moves a specific song in the queue from one position to another.
        Example: ?move 5 2 will move the song at position 5 to position 2.
        """
        if not await self.is_allowed_channel(ctx):
            return
        if not await self.is_allowed_role(ctx):
            return

        player = self.get_player_cog()
        if not player:
            await ctx.send("❌ MusicPlayer cog is not loaded.")
            return

        guild_id = ctx.guild.id
        queue = player.song_queue.get(guild_id, [])

        if not queue:
            await ctx.send("📭 The queue is empty.")
            return

        from_index = from_pos - 1
        to_index = to_pos - 1

        if from_index < 0 or from_index >= len(queue):
            await ctx.send(f"❌ Invalid from-position. Choose between 1 and {len(queue)}.")
            return
        if to_index < 0 or to_index >= len(queue):
            await ctx.send(f"❌ Invalid to-position. Choose between 1 and {len(queue)}.")
            return
        if from_index == to_index:
            await ctx.send("❌ The song is already at that position.")
            return

        song = queue.pop(from_index)
        queue.insert(to_index, song)

        await ctx.send(f"↕️ Moved **{song['title']}** from position {from_pos} to {to_pos}.")

async def setup(bot):
    await bot.add_cog(QueueManager(bot))