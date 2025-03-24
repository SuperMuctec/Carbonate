import discord
from discord import app_commands
from discord.ext import commands

# Enable necessary intents
intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    
    print(f"✅ Logged in as {bot.user}")


@bot.command(aliases=['hi','yow'])
async def hello(ctx):
        await ctx.send(f"Hello there, {ctx.author.mention}")
        
@bot.hybrid_command(name="syncslash")
@commands.has_guild_permissions(administrator=True)
async def sync_slash(ctx: commands.context.Context):
    await bot.tree.sync()
    
    if ctx.interaction:
        await ctx.interaction.response.send_message("Slash commands synced!", ephemeral=True)
    else:
        await ctx.send("Slash commands synced!")
# Handle missing permissions error
@sync_slash.error
async def sync_slash_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        if ctx.interaction:
            await ctx.interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
        else:
            await ctx.send("❌ You don't have permission to use this command!")


@bot.hybrid_command(name="kick")
@discord.app_commands.describe(member="The user to kick", reason="Reason for kick (optional)")
@commands.has_guild_permissions(kick_members=True)
async def kick(ctx: commands.Context, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason=reason)
        if ctx.interaction:
            await ctx.interaction.response.send_message(f"✅ {member.mention} has been kicked! Reason: {reason}", ephemeral=True)
        else:
            await ctx.send(f"✅ {member.mention} has been kicked! Reason: {reason}")
    
    except discord.Forbidden:
        if ctx.interaction:
            await ctx.interaction.response.send_message("❌ I can't kick this member due to role hierarchy.", ephemeral=True)
        else:
            await ctx.send("❌ I can't kick this member due to role hierarchy.")
    
    except Exception as e:
        if ctx.interaction:
            embed = discord.Embed("❌ An error occurred",description=e, color= discord.color.Random())
            await ctx.interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed("❌ An error occurred",description=e, color= discord.color.Random())
            await ctx.send(embed=embed)

# Missing Permissions Handler
@kick.error
async def kick_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        if ctx.interaction:
            await ctx.interaction.response.send_message("❌ You don't have permission to kick users!", ephemeral=True)
        else:
            await ctx.send("❌ You don't have permission to kick users!")

@bot.hybrid_command(name="ban")
@discord.app_commands.describe(member="The user to ban", reason="Reason for ban (optional)")
@commands.has_guild_permissions(ban_members=True)
async def ban(ctx: commands.Context, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        if ctx.interaction:
            await ctx.interaction.response.send_message(f"✅ {member.name} has been banned! Reason: {reason}", ephemeral=True)
        else:
            await ctx.send(f"✅ {member.name} has been banned! Reason: {reason}")
    
    except discord.Forbidden:
        if ctx.interaction:
            await ctx.interaction.response.send_message("❌ I can't ban this member due to role hierarchy.", ephemeral=True)
        else:
            await ctx.send("❌ I can't ban this member due to role hierarchy.")
    
    except Exception as e:
        if ctx.interaction:
            embed = discord.Embed("❌ An error occurred",description=e, color= discord.color.Random())
            await ctx.interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed("❌ An error occurred",description=e, color= discord.color.Random())
            await ctx.send(embed=embed)

# Missing Permissions Handler
@ban.error
async def ban_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        if ctx.interaction:
            await ctx.interaction.response.send_message("❌ You don't have permission to ban users!", ephemeral=True)
        else:
            await ctx.send("❌ You don't have permission to ban users!")

@bot.hybrid_command(name="unban")
@commands.has_permissions(ban_members=True)
@discord.app_commands.describe(user_id="The ID of the user to unban")
async def unban(ctx: commands.Context, user_id: int):
    try:
        user = await bot.fetch_user(user_id)  # Get user object from ID
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.name} has been unbanned!")
    except discord.NotFound:
        await ctx.send("❌ User not found in the ban list.", ephemeral=True)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unban users.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"⚠️ An error occurred: {e}", ephemeral=True)

def run(token):
    bot.run(token)
