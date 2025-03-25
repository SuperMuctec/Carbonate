import os
import pathlib
import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
import discord
import dotenv
from bot import find_all_modules_in_directory, Carbonate

dotenv.load_dotenv()

TOKEN = os.getenv('token')

modules_directory = pathlib.Path(__file__).parent.joinpath('modules').resolve()

initial_extensions = find_all_modules_in_directory(modules_directory)
initial_extensions = [f'modules.{extension}' for extension in initial_extensions]

bot = Carbonate(intents=discord.Intents.all(), initial_extensions=initial_extensions)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    with sqlite3.connect('roles.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT Server, Roleid FROM ROLES WHERE Server = ?", (str(member.guild.id),))
        result = cur.fetchone()

        if result:
            role_id = int(result[1])
            role = discord.utils.get(member.guild.roles, id=role_id)
            if role:
                try:
                    await member.add_roles(role)
                    print(f"Assigned role {role.name} to {member.name}.")
                except discord.Forbidden:
                    print(f"Bot lacks permissions to assign role {role.name}.")
                except Exception as e:
                    print(f"Error assigning role: {e}")
            else:
                print(f"Role with ID {role_id} not found in {member.guild.name}.")

@bot.command(aliases=['hi', 'yo'])
async def hello(ctx):
    await ctx.send(f"Hello there, {ctx.author.mention}")


bot.run(TOKEN)
