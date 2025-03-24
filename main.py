import os
import discord
from discord import app_commands
from discord.ext import commands
import traceback, datetime
from dotenv import load_dotenv

load_dotenv()

# Enable necessary intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=os.environ.get("prefix","!"), intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await load_extensions()


@bot.event
async def on_command_error(ctx, error):
    traceback.print_exception(type(error), error, error.__traceback__)
    # if isinstance(error, func.NotDev):
    #    await ctx.send(
    #        embed=func.Embed()
    #        .title("Error")
    #        .description("This command is only available to developers.")
    #        .color(0xF38BA8)
    #        .embed,
    #        ephemeral=True,
    #    )
    #    return
    if isinstance(error, commands.CommandNotFound):
        # was gonna add this, but ngl it kinda sucks if you have multiple bots with the same prefix in your server.
        # await ctx.invoke(bot.get_command("help"), args="")
        return
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            color=0xF38BA8,
            title="Error",
            description="You do not have permission to use this command.",
        )
        await ctx.send(
            embed=embed,
            ephemeral=True,
        )
        return
    if isinstance(error, commands.CommandOnCooldown):
        sec = error.retry_after
        date = datetime.datetime.now() + datetime.timedelta(seconds=sec)
        embed = discord.Embed(
            color=0xF38BA8,
            title="Error",
            description="This command is on cooldown. Please try again <t:{round(date.timestamp())}:R>",
        )
        await ctx.send(
            embed=embed,
            ephemeral=True,
        )
        return
    # @SuperMuctec add more error handling here if needed

    # Get the deepest exception by walking through the __cause__ chain
    original_error = error
    while hasattr(original_error, "__cause__") and original_error.__cause__ is not None:
        original_error = original_error.__cause__

    error_traceback = traceback.extract_tb(original_error.__traceback__)[-1]
    filename = error_traceback.filename
    line_number = error_traceback.lineno
    line = error_traceback.line

    embed = discord.Embed(
        color=0xF38BA8,
        title="Error",
        description=f"**Error:** ```{original_error}```\n**File:** {filename}\n**Line {line_number}:** `{line}`",
    )
    await ctx.send(
        embed=embed,
        ephemeral=True,
    )


@bot.hybrid_command(aliases=["hi", "yow"])
async def hello(ctx):
    await ctx.send(f"Hello there, {ctx.author.mention}")


@bot.hybrid_command(name="syncslash")
@commands.has_guild_permissions(
    administrator=True
)  # im too lazy to change this, but its really unsafe. only developers should have access.
# https://github.com/Spelis/LunaBot/blob/bb8cc6e89785ae2441e3439b43b9a4fecd80ebae/func.py#L37C1-L53C1
async def sync_slash(ctx: commands.context.Context):
    await bot.tree.sync()
    await ctx.send("Slash commands synced!", ephemeral=True)


initial_extensions = list(map(lambda x: x[:-3], os.listdir("./cogs")))
if "__pycach" in initial_extensions:
    initial_extensions.remove("__pycach")  # remove __pycache__
    
async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension("cogs." + extension)
            print(f'Successfully loaded extension "{extension}"')
        except Exception as e:
            traceback.print_exc()
            print(
                f'Failed to load extension "{extension}". Check error above'
            )

if __name__ == "__main__":
    bot.run(os.environ.get("token"))
