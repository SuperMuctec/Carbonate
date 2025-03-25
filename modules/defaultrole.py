import discord
from discord.ext import commands
import sqlite3


class DefaultRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You have missing permissions [Administrator]")
    
    @commands.hybrid_command(name="setdefaultrole")
    @commands.has_permissions(administrator=True)
    @discord.app_commands.describe(role="The default role")
    async def setdefaultrole(self, ctx: commands.Context, role: discord.Role):
        with sqlite3.connect('roles.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT Server FROM ROLES WHERE Server = ?", (ctx.guild.id,))
            if cur.fetchone():
                await ctx.send("Default Role already set.")
                return

            cur.execute("INSERT INTO ROLES (Server, Roleid) VALUES (?, ?)", (ctx.guild.id, role.id))
            conn.commit()
            await ctx.send("✅ Default role initialized.")

    @commands.hybrid_command(name="deletedefaultrole")
    @commands.has_permissions(administrator=True)
    async def deletedefaultrole(self, ctx: commands.Context):
        conn = sqlite3.connect('roles.db')
        cur = conn.cursor()
        cur.execute("SELECT Server FROM ROLES")
        guildids = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT Roleid FROM ROLES")
        channelids = [row[0] for row in cur.fetchall()]
        srver = ctx.guild.id

        if str(ctx.guild.id) in guildids:
            query = "DELETE FROM ROLES WHERE Server = ?"
            cur.execute(query, (srver,))
            conn.commit()
            conn.close()
            await ctx.send("Default Role deleted for this server")
        else:
            await ctx.channel.send("Default Role not initialized do !defaultrole-declare help for more")
async def setup(bot: commands.Bot):
    await bot.add_cog(DefaultRole(bot))

    