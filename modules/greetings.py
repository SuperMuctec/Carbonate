import discord
from discord.ext import commands
import sqlite3


class Greetings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name = "setwelcome")
    @commands.has_permissions(administrator = True)
    @discord.app_commands.describe(channel="The welcome channel")
    async def setwelcome(self, ctx: commands.Context, channel: discord.TextChannel):
        srver = ctx.guild.id
        role = channel.id
        conn = sqlite3.connect('serverdat.db')
        cur = conn.cursor()
        cur.execute("SELECT ServerId FROM WELCOME")
        guildids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT Welcome FROM WELCOME")
        roleids = [row[0] for row in cur.fetchall()]

        if srver not in guildids:
            if ctx.guild.get_channel(int(role)) != None:
                cur.execute("INSERT INTO WELCOME (ServerId, Welcome) VALUES (?, ?)", (srver, role))
                conn.commit()
                conn.close() 
                await ctx.send("Default Welcome Channel initialized")
            else:
                await ctx.send("Channel does not exist")
        else:
            await ctx.send("Default Welcome Channel already initialized, remove them using /removewelcome")

async def setup(bot: commands.Bot):
    await bot.add_cog(Greetings(bot))
