import discord
from discord import app_commands
from discord.ext import commands

# Enable necessary intents
intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user} | Slash commands synced!")


@bot.command()
async def hello(ctx):
        await ctx.send(f"Hello there, {ctx.author.mention}")

def run(token):
    bot.run(token)
