import os
import pathlib
import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
import discord
import dotenv
from bot import find_all_modules_in_directory, Carbonate
import google.generativeai as genai
import asyncio
import requests

dotenv.load_dotenv()

TOKEN = os.getenv('token')
GENAI = os.getenv('gemini')

modules_directory = pathlib.Path(__file__).parent.joinpath('modules').resolve()

initial_extensions = find_all_modules_in_directory(modules_directory)
initial_extensions = [f'modules.{extension}' for extension in initial_extensions]

bot = Carbonate(intents=discord.Intents.all(), initial_extensions=initial_extensions)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    activity = discord.Game(name="/trivia | {} servers".format(len(bot.guilds)))
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_member_join(member):
    srver = member.guild.id
    with sqlite3.connect('serverdat.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT ServerId, Welcome FROM WELCOME")
        results = cur.fetchall()

        guildids = [row[0] for row in results]
        channelids = [row[1] for row in results]
        print(f"Welcome Guild IDs: {guildids}")
        print(f"Welcome Channel IDs: {channelids}")

        if str(srver) in guildids:
            channelid = channelids[guildids.index(str(srver))]
            channel = member.guild.get_channel(int(channelid))
            if channel:
                await channel.send(f"Welcome to {member.guild}, {member.mention}! 🎉 We're glad to have you here!")
            else:
                print(f"Channel {channelid} not found.")



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

@bot.event
async def on_member_remove(member):
    srver = member.guild.id
    conn = sqlite3.connect('serverdat.db')
    cur = conn.cursor()
    cur.execute("SELECT ServerId FROM GOODBYE")
    guildids = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT GoodBye FROM GOODBYE")
    channelids = [row[0] for row in cur.fetchall()]
    print(guildids)
    print(channelids)
    
    if str(srver) in guildids:
        channelid = channelids[guildids.index(str(srver))]
        channel = member.guild.get_channel(int(channelid))
        await channel.send(f"GoodBye from {member.guild}, {member.name}! We're sad to lose you 😭")
        conn.close()

@bot.command(aliases=['hi', 'yo'])
async def hello(ctx):
    await ctx.send(f"Hello there, {ctx.author.mention}")

@bot.hybrid_command(name = "chatgpt")
@discord.app_commands.describe(prompt = "The question you want to ask to chatgpt (basically gemini)")
async def chatgpt(ctx:commands.Context, prompt: str):
    try:
        genai.configure(api_key=GENAI)
        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(f"{prompt} + under 2000 characters")
        await ctx.send(response.text)
    except:
        await ctx.send(
            "The response is too long ( > 2000 characters) and is restricted by discord guidelines")

@bot.hybrid_command(name = "translate")
@discord.app_commands.describe(language = "The language you want to tranlate to", text = "The text you want to translate")
async def translate(ctx:commands.Context, language: str, text: str):
    genai.configure(api_key=GENAI)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(f"translate {text} to {language} give only answer")

    await ctx.send(f"The Translated text is: {response.text}")

@bot.hybrid_command(name = "trivia")
async def trivia(ctx:commands.Context):
    response = requests.get('https://opentdb.com/api.php?amount=1')
    question_data = response.json()['results'][0]
    question = question_data['question']
    correct_answer = question_data['correct_answer']
    question = question.replace("quot", '""')
    msg = ctx.send(f"Trivia Time: {question}")
    await asyncio.sleep(10)
    await msg.reply(f"The correct answer was: {correct_answer}")
bot.run(TOKEN)
