import discord
from discord.ext import commands
import sqlite3
import pathlib
import subprocess
import re

class ServerInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.update(member)

    @commands.hybrid_command(name="setstatistics")
    @commands.has_permissions(administrator = True)
    @discord.app_commands.describe(channel = "The statistics channel of the server")
    async def statset(self, ctx:commands.Context, channel: discord.TextChannel):
        srver = ctx.guild.id
        role = channel.id
        conn = sqlite3.connect('serverdat.db')
        cur = conn.cursor()
        cur.execute("SELECT ServerId FROM STATISTICS")
        guildids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT Statistics FROM STATISTICS")
        roleids = [row[0] for row in cur.fetchall()]

        if srver not in guildids:
            if ctx.guild.get_channel(int(role)) != None:
                cur.execute("INSERT INTO STATISTICS (ServerId, Statistics) VALUES (?, ?)", (srver, role))
                conn.commit()
                conn.close() 
                await ctx.send("Default Statistics Channel initialized")
            else:
                await ctx.send("Channel does not exist")
        else:
            await ctx.send("Default Statistics Channel already initialized, remove them using /removestatistics")

    async def update(self, member: discord.Member):
        srver = member.guild.id
        conn = sqlite3.connect('serverdat.db')
        cur = conn.cursor()
        cur.execute("SELECT ServerId FROM STATISTICS")
        guildids = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT Statistics FROM STATISTICS")
        channelids = [row[0] for row in cur.fetchall()]
        if str(srver) in guildids:
            chaid = int(channelids[guildids.index(str(srver))])
            channel = self.bot.get_channel(chaid)
            await channel.purge()
            guild = member.guild
            server_name = guild.name
            total_members = guild.member_count
            online_members = sum(1 for member in guild.members if member.status == discord.Status.online)
            text_channels = sum(1 for channel in guild.channels if isinstance(channel, discord.TextChannel))
            voice_channels = sum(1 for channel in guild.channels if isinstance(channel, discord.VoiceChannel))
            server_created_on = guild.created_at.strftime('%Y-%m-%d')

        # Create the response message
            stats_message = (
                f"=== Server Statistics ===\n"
                f"🏠 **Server Name:** {server_name}\n"
                f"👥 **Total Members:** {total_members}\n"
                f"✅ **Online Members:** {online_members}\n"
                f"🗨️ **Text Channels:** {text_channels}\n"
                f"🎤 **Voice Channels:** {voice_channels}\n"
                f"📅 **Server Created On:** {server_created_on}"
            )
            await channel.send(stats_message)
            conn.close()
        else:
            pass
    @commands.hybrid_command(name="removestatistics")
    @commands.has_permissions(administrator = True)
    async def removestats(self, ctx:commands.Context):
        srver = ctx.guild.id
        conn = sqlite3.connect('serverdat.db')
        cur = conn.cursor()
        cur.execute("SELECT ServerId FROM STATISTICS")
        guildids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT Statistics FROM STATISTICS")
        roleids = [row[0] for row in cur.fetchall()]
        if str(ctx.guild.id) in guildids:
            query = "DELETE FROM STATISTICS WHERE ServerId = ?"
            cur.execute(query, (srver,))
            conn.commit()
            conn.close()
            await ctx.send("Statistics channel deleted for this server")
        else:
            await ctx.send("Statistics Channel not initialized do /setstatistics help for more")
    
    
    
async def setup(bot: commands.Bot):
    await bot.add_cog(ServerInfo(bot))
