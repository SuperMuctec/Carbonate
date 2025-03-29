import discord
from discord.ext import commands
import sqlite3


class Counter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.count = 0  # Stores the last correct count
        self.lastuser = None  # Stores the last person who counted
        self.creset = False
    @commands.Cog.listener()
    async def on_message(self, message):

        conn = sqlite3.connect('counter.db')
        cur = conn.cursor()
        cur.execute("SELECT ServerID FROM Counter")
        guildids = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT ChannelID FROM Counter")
        channelids = [row[0] for row in cur.fetchall()]
        
        if message.channel.id in channelids:
            if message.author.bot:  # Ignore bot messages
                return 

            if message.content.isdigit():  # Check if the message is a number
                num = int(message.content)

                if self.count == 0:  # First message starts the counting
                    if num != 1:  # Ignore wrong starts
                        return
                    
                    await message.channel.send(f"Counting has been started by {message.author.mention}")
                    self.count = 1
                    self.lastuser = message.author.id
                    return  # Stop here to prevent further checks

                if num == self.count + 1:  # Correct next number
                    if message.author.id != self.lastuser:  # Different user
                        self.count += 1
                        self.lastuser = message.author.id
                        print(f"Count updated: {self.count}")
                    else:
                        await message.channel.send(
                            f"{message.author.mention}, you can't count twice in a row! The counting was till {self.count}."
                        )
                        self.count = 0
                        self.lastuser = None
                        self.creset = False
                else:
                    self.creset = True
                    await message.channel.send(
                        f"{message.author.mention} ruined the counting! The correct number was {self.count + 1}. Restarting from 1!"
                    )
                    self.count = 0
                    self.lastuser = None
        else:
            print("Else 58")
            return

    @commands.hybrid_command(name="set-counting-channel")
    @commands.has_permissions(administrator=True)
    @discord.app_commands.describe(channel="The counting channel")
    async def setdefaultrole(self, ctx: commands.Context, channel: discord.TextChannel):
        with sqlite3.connect('counter.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT ChannelID FROM Counter WHERE ServerID = ?", (ctx.guild.id,))
            if cur.fetchone():
                await ctx.send("Counting Channel already set.")
                return

            cur.execute("INSERT INTO Counter (ServerID, ChannelID) VALUES (?, ?)", (ctx.guild.id, channel.id))
            conn.commit()
            await ctx.send("✅ Default counting channel initialized.")

    @commands.hybrid_command(name="delete-counting-channel")
    async def deletedefaultrole(self, ctx: commands.Context):
        conn = sqlite3.connect('counter.db')
        cur = conn.cursor()
        cur.execute("SELECT ServerID FROM Counter")
        guildids = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT ChannelID FROM Counter")
        channelids = [row[0] for row in cur.fetchall()]
        srver = ctx.guild.id
        print(guildids)
        if ctx.guild.id in guildids:
            query = "DELETE FROM Counter WHERE ServerID = ?"
            cur.execute(query, (srver,))
            conn.commit()
            conn.close()
            await ctx.send("Counting Channel deleted for this server")
        else:
            await ctx.channel.send("Default Role not initialized do /set-counting-channel for more")
            conn.close()
async def setup(bot: commands.Bot):
    await bot.add_cog(Counter(bot))