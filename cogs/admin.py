from discord.ext import commands
import discord

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.hybrid_command(name="kick")
    #@discord.app_commands.describe(
    #    member="The user to kick", reason="Reason for kick (optional)"
    #)
    @commands.has_guild_permissions(kick_members=True)
    async def kick(
        self,ctx: commands.Context, member: discord.Member, reason: str = "No reason provided"
    ):
        try:
            await member.kick(reason=reason)
            await ctx.send(
                f"✅ {member.mention} has been kicked! Reason: {reason}", ephemeral=True
            )

        except discord.Forbidden:
            await ctx.send(
                "❌ I can't kick this member due to role hierarchy.", ephemeral=True
            )

        except Exception as e:
            embed = discord.Embed(
                title="❌ An error occurred", description=e, color=discord.Colour.random()
            )
            await ctx.send(embed=embed, ephemeral=True)


    @commands.hybrid_command(name="ban")
    ##@discord.app_commands.describe(
    ##    member="The user to ban", reason="Reason for ban (optional)"
    ##)
    @commands.has_guild_permissions(ban_members=True)
    async def ban(
        self,ctx: commands.Context, member: discord.Member, reason: str = "No reason provided"
    ):
        try:
            await member.ban(reason=reason)
            await ctx.send(
                f"✅ {member.name} has been banned! Reason: {reason}", ephemeral=True
            )

        except discord.Forbidden:
            await ctx.send(
                "❌ I can't ban this member due to role hierarchy.", ephemeral=True
            )

        except Exception as e:
            embed = discord.Embed(
                "❌ An error occurred", description=e, color=discord.color.Random()
            )
            await ctx.send(embed=embed, ephemeral=True)


    @commands.hybrid_command(name="unban")
    @commands.has_permissions(ban_members=True)
    #@discord.app_commands.describe(user_id="The ID of the user to unban")
    async def unban(self,ctx: commands.Context, user: discord.User):
        try:
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user.name} has been unbanned!", ephemeral=True)
        except discord.NotFound:
            await ctx.send("❌ User not found in the ban list.", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
