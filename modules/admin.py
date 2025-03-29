import discord
from discord.ext import commands
import sqlite3
import traceback

class Administrator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @commands.hybrid_command(name="syncslash")
    @commands.has_permissions(administrator=True)
    async def sync_slash(self, ctx: commands.Context):
        await self.bot.tree.sync()
        response = "Slash commands synced!"
        if ctx.interaction:
            await ctx.interaction.response.send_message(response, ephemeral=True)
        else:
            await ctx.send(response)

    @sync_slash.error
    async def sync_slash_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!", ephemeral=True)

    @commands.hybrid_command(name="kick")
    @discord.app_commands.describe(member="The user to kick", reason="Reason for kick (optional)")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, reason: str = "No reason provided"):
        try:
            await member.kick(reason=reason)
            await ctx.send(f"✅ {member.mention} has been kicked! Reason: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ I can't kick this member due to role hierarchy.")
        except Exception as e:
            embed = discord.Embed(title="❌ An error occurred", description=str(e), color=discord.Color.red())
            await ctx.send(embed=embed)

    @kick.error
    async def kick_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to kick users!")

    @commands.hybrid_command(name="ban")
    @discord.app_commands.describe(member="The user to ban", reason="Reason for ban (optional)")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: str = "No reason provided"):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"✅ {member.mention} has been banned! Reason: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ I can't ban this member due to role hierarchy.")
        except Exception as e:
            embed = discord.Embed(title="❌ An error occurred", description=str(e), color=discord.Color.red())
            await ctx.send(embed=embed)

    @ban.error
    async def ban_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to ban users!")

    @commands.hybrid_command(name="unban")
    @commands.has_permissions(ban_members=True)
    @discord.app_commands.describe(user="The ID of the user to unban")
    async def unban(self, ctx: commands.Context, user: discord.User):
        try:
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user.name} has been unbanned!")
        except discord.NotFound:
            await ctx.send("❌ User not found in the ban list.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users.")
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}")

    @commands.hybrid_command(name="dmall")
    @commands.has_permissions(administrator = True)
    @commands.cooldown(1, 1800, commands.BucketType.user)
    @discord.app_commands.describe(message="The message you want to send to all the members in the server")
    async def dmall(self, ctx: commands.Context, message: str):
        await ctx.defer()
        failed = ""
        for member in ctx.guild.members:
            if not member.bot:  # Ignore bots
                try:
                    await member.send(message)
                except discord.Forbidden:
                    failed += f"{member.name}\n"
        failed = "```" + failed + "```"
        await ctx.send(f"All members have been dmed, failed user list has been sent to {ctx.author.mention} in dms")
        await ctx.author.send(failed)

    @dmall.error
    async def dmall_error(self, ctx, error):
        """Handles errors for the /work command."""
        if isinstance(error, commands.CommandOnCooldown):
            remaining = int(error.retry_after)
            hours, remainder = divmod(remaining, 3600)
            minutes, seconds = divmod(remainder, 60)

            time_str = (
                f"{hours}h {minutes}m {seconds}s" if hours > 0 else
                f"{minutes}m {seconds}s" if minutes > 0 else
                f"{seconds}s"
            )

            await ctx.send(f"⏳ You are on cooldown! Try again in **{time_str}**.")
        else:
            await ctx.send(f"⚠️ An error occurred: {error}")
            print(f"Error in /work command:\n{traceback.format_exc()}")
async def setup(bot: commands.Bot):
    await bot.add_cog(Administrator(bot))
