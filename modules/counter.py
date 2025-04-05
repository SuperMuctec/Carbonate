from datetime import datetime, timedelta
import pathlib
import sqlite3
import aiosqlite

import discord
from discord.ext import commands


class CounterService:
    def __init__(self, database: pathlib.Path | str):
        self.database = str(database)

    async def get_counting_channel(self, guild_id: int) -> int | None:
        async with aiosqlite.connect(self.database) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT ChannelID FROM Counter WHERE ServerID = ?", (guild_id,)
                )
                result = await cur.fetchone()
                if result:
                    return result[0]
                else:
                    return None

    async def update_counting_channel(self, guild_id: int, channel_id: int):
        async with aiosqlite.connect(self.database) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO Counter (ServerID, ChannelID) VALUES (?, ?)",
                    (guild_id, channel_id),
                )
                await conn.commit()

    async def delete_counting_channel(self, guild_id: int):
        async with aiosqlite.connect(self.database) as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM Counter WHERE ServerID = ?", (guild_id,))
                await conn.commit()

    async def get_count(self, guild_id: int) -> int | None:
        async with aiosqlite.connect(self.database) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT LastNumber FROM Counter WHERE ServerID = ?", (guild_id,)
                )
                result = await cur.fetchone()
                if result:
                    return result[0]
                else:
                    return None

    async def update_count(self, guild_id: int, count: int):
        async with aiosqlite.connect(self.database) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE Counter SET LastNumber = ? WHERE ServerID = ?",
                    (count, guild_id),
                )
                await conn.commit()

    async def get_last_user(self, guild_id: int) -> int | None:
        async with aiosqlite.connect(self.database) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT LastUser FROM Counter WHERE ServerID = ?", (guild_id,)
                )
                result = await cur.fetchone()
                if result:
                    return result[0]
                else:
                    return None

    async def update_last_user(self, guild_id: int, user_id: int):
        async with aiosqlite.connect(self.database) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE Counter SET LastUser = ? WHERE ServerID = ?",
                    (user_id, guild_id),
                )
                await conn.commit()


class CounterAntiAbuse:
    def __init__(self):
        self.violations = []
        self.notified = False

    async def notify_abuse(self, member: discord.Member):
        if not self.notified:
            dm_channel = await member.create_dm()
            try:
                await dm_channel.send(
                    "You have been detected as a potential spammer. You will be banned from using the counter for 15 minutes.\nIf you believe this is a false positive, you can contact a developer to help improve this system."
                )
            except discord.Forbidden:
                print(
                    f"Member {member.id} has DMs disabled. Cannot notify of counter ban."
                )
                return
            finally:
                self.notified = True

    def add_violation(self) -> None:
        self.violations.append(discord.utils.utcnow())

    def _remove_old_violations(self, lifetime: timedelta) -> None:
        self.violations = [
            v for v in self.violations if discord.utils.utcnow() - v < lifetime
        ]

    def get_violations(self, lifetime: timedelta) -> int:
        self._remove_old_violations(lifetime)
        # Since we're pruning the list, we can simply return the new length
        return len(self.violations)


class Counter(commands.Cog):
    ANTI_ABUSE_LIFETIME = timedelta(minutes=15) # How far in the fast are we looking for violations?
    ANTI_ABUSE_THRESHOLD = 3 # How many violations must the user have to be banned?
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.service = CounterService("counter.db")
        self.anti_abuse: dict[discord.Member, CounterAntiAbuse] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:  # Ignore DMs
            return

        if message.author.bot:  # Ignore bot messages
            return

        channel_id = await self.service.get_counting_channel(message.guild.id)
        if channel_id is None:
            return

        if message.author not in self.anti_abuse:
            self.anti_abuse[message.author] = CounterAntiAbuse()

        if (
            self.anti_abuse.get(message.author).get_violations(self.ANTI_ABUSE_LIFETIME)
            > self.ANTI_ABUSE_THRESHOLD
        ):
            # We ignore people who often count wrongly to avoid spamming
            await self.anti_abuse.get(message.author).notify_abuse(message.author)
            return

        message_content = message.content.strip()

        if not message_content.isdigit():
            return

        proposed_next_count = int(message.content)

        current_count = await self.service.get_count(message.guild.id)
        if current_count is None:
            current_count = 0

        last_user = await self.service.get_last_user(message.guild.id)
        if last_user is None:
            last_user = 0

        if message.author.id == last_user:
            await message.add_reaction("❌")
            self.anti_abuse.get(message.author).add_violation()
            await self.service.update_count(message.guild.id, 0)
            await self.service.update_last_user(message.guild.id, 0)
            return

        if proposed_next_count != current_count + 1:
            await message.add_reaction("❌")
            self.anti_abuse.get(message.author).add_violation()
            await self.service.update_count(message.guild.id, 0)
            await self.service.update_last_user(message.guild.id, 0)
            return

        await self.service.update_count(message.guild.id, proposed_next_count)
        await self.service.update_last_user(message.guild.id, message.author.id)

        await message.add_reaction("✅")

    @commands.hybrid_group(
        name="counting",
        usage="counting <set [channel]|delete>",
        description="Lets you manage the counting module.",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def counting(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.reply("Please specify a subcommand.")

    @counting.command(name="set")
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 15, commands.BucketType.member)
    @discord.app_commands.describe(channel="The counting channel")
    async def _set_counting_channel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        channel_id = await self.service.get_counting_channel(ctx.guild.id)
        if channel_id is not None:
            await ctx.reply(
                "Counting Channel already set. Use `/counting delete` to unset it."
            )
            return

        await self.service.update_counting_channel(ctx.guild.id, channel.id)
        await ctx.reply(f"Counting Channel set to {channel.mention}")

    @counting.command(name="delete")
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 15, commands.BucketType.member)
    async def _delete_counting_channel(self, ctx: commands.Context):
        channel_id = await self.service.get_counting_channel(ctx.guild.id)
        if channel_id is None:
            await ctx.reply("Counting Channel not set. Use `/counting set` to set it.")
            return

        await self.service.delete_counting_channel(ctx.guild.id)
        await ctx.reply(
            "Counting Channel unset. You can use `/counting set` to set it again."
        )

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                "❌ You are on cooldown. Please try again later.", ephemeral=True
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "❌ You don't have permission to use this command!", ephemeral=True
            )


async def setup(bot: commands.Bot):

    await bot.add_cog(Counter(bot))
