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
    
    @setwelcome.error
    async def welcomerr(self, ctx:commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have administrator permissions!")

    @commands.hybrid_command(name = "removewelcome")
    @commands.has_permissions(administrator = True)
    @discord.app_commands.describe()
    async def removewelcome(self, ctx:commands.Context):
        conn = sqlite3.connect('serverdat.db')
        cur = conn.cursor()
        cur.execute("SELECT ServerId FROM WELCOME")
        guildids = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT Welcome FROM WELCOME")
        channelids = [row[0] for row in cur.fetchall()]
        srver = ctx.guild.id

        if str(ctx.guild.id) in guildids:
            query = "DELETE FROM WELCOME WHERE ServerId = ?"
            cur.execute(query, (srver,))
            conn.commit()
            conn.close()
            await ctx.send("Welcome channel deleted for this server")
        else:
            await ctx.send("Welcome Channel not initialized do /welcome for more")
    @removewelcome.error
    async def delwelcomerr(self, ctx:commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have administrator permissions!")

    @commands.hybrid_command(name = "setgoodbye")
    @commands.has_permissions(administrator = True)
    @discord.app_commands.describe(channel="The goodbye channel")
    async def setgoodbye(self, ctx: commands.Context, channel: discord.TextChannel):
        srver = ctx.guild.id
        role = channel.id
        conn = sqlite3.connect('serverdat.db')
        cur = conn.cursor()
        cur.execute("SELECT ServerId FROM GOODBYE")
        guildids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT GoodBye FROM GOODBYE")
        roleids = [row[0] for row in cur.fetchall()]

        if srver not in guildids:
            if ctx.guild.get_channel(int(role)) != None:
                cur.execute("INSERT INTO GOODBYE (ServerId, GoodBye) VALUES (?, ?)", (srver, role))
                conn.commit()
                conn.close() 
                await ctx.send("Default Goodbye Channel initialized")
            else:
                await ctx.send("Channel does not exist")
        else:
            await ctx.send("Default Goodbye Channel already initialized, remove them using /removegoodbye")
    
    @setgoodbye.error
    async def delgoodbyerr(self, ctx:commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have administrator permissions!")

    @commands.hybrid_command(name = "removegoodbye")
    @commands.has_permissions(administrator = True)
    @discord.app_commands.describe()
    async def removegoodbye(self, ctx:commands.Context):
        conn = sqlite3.connect('serverdat.db')
        cur = conn.cursor()
        cur.execute("SELECT ServerId FROM GOODBYE")
        guildids = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT GoodBye FROM GOODBYE")
        channelids = [row[0] for row in cur.fetchall()]
        srver = ctx.guild.id

        if str(ctx.guild.id) in guildids:
            query = "DELETE FROM GOODBYE WHERE ServerId = ?"
            cur.execute(query, (str(srver),))
            conn.commit()
            conn.close()
            await ctx.channel.send("Goodbye channel deleted for this server")
        else:
            await ctx.channel.send("Goodbye Channel not initialized do /setgoodbye")
    @removegoodbye.error
    async def delgoodbyeerr(self, ctx:commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have administrator permissions!")
async def setup(bot: commands.Bot):
    await bot.add_cog(Greetings(bot))
