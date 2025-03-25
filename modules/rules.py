import discord
from discord.ext import commands
import sqlite3


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You have missing permissions [Administrator]")
    
    @commands.hybrid_command(name="setrules")
    @commands.has_permissions(administrator=True)
    @discord.app_commands.describe(
        channel="The Rules Channel", message="The Rules message ID"
    )
    async def set_rules(self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        message: str,
    ):
        with sqlite3.connect("rules.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM RULES WHERE id = ?", (ctx.guild.id,))
            if cur.fetchone():
                await ctx.send(
                    "Rules already initialized. Use `/removerules` first."
                )
                return

            cur.execute(
                "INSERT INTO RULES (id, channelid, messageid) VALUES (?, ?, ?)",
                (ctx.guild.id, str(channel.id), str(message)),
            )
            conn.commit()
            await ctx.send("✅ Rules initialized.")

    @commands.hybrid_command(name="rules")
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def rules(self, ctx: commands.Context):
        with sqlite3.connect("rules.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT channelid, messageid FROM RULES WHERE id = ?",
                (ctx.guild.id,),
            )
            result = cur.fetchone()

            if result:
                print(result)
                print(result[0], type(result[0]))
                channel = self.bot.get_channel(int(result[0]))
                print(channel)
                if channel:
                    try:
                        message = await channel.fetch_message(int(result[1]))
                        await ctx.send(message.content)
                    except discord.NotFound:
                        await ctx.send("❌ The rules message was not found.")
                else:
                    await ctx.send("❌ The rules channel was not found.")
            else:
                await ctx.send("Rules have not been initialized.")

    @commands.hybrid_command(name="removerules")
    @commands.has_permissions(administrator=True)
    async def removerules(self, ctx: commands.Context):
        with sqlite3.connect("rules.db") as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM RULES WHERE id = ?", (ctx.guild.id,))
            conn.commit()
            await ctx.send("✅ Rules deleted.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Rules(bot))
