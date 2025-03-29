import discord
from discord.ext import commands
import sqlite3
import random
import aiosqlite
import traceback

class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name = "enable-economy")
    async def enable(self, ctx:commands.Context):
        conn = sqlite3.connect("economy.db")
        cur = conn.cursor()

        tableName = str(ctx.guild.id)
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
        result = cur.fetchone()
        if result is None:
            cur.execute(f"""
                        CREATE TABLE "{ctx.guild.id}" (
                            "UserID"	INTEGER,
                            "Balance"	REAL,
                            "Work"	REAL
                        );
                        """)
            conn.commit()
            conn.close()

            await ctx.send("Economy Successfully initialized for this server")
        else:
            await ctx.send("Economy already enabled for this server")



    @commands.hybrid_command(name="work")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @discord.app_commands.describe(time="Hours to work (max 3)")
    async def work(self, ctx: commands.Context, time: int):
        await ctx.defer()
        if time > 8:
            await ctx.send("You cannot work for more than 8 hours...")
            self.work.reset_cooldown(ctx)
            return
        else:
            money_per_hour = random.randint(1, 21)
            total_earnings = money_per_hour * time

            conn = await aiosqlite.connect("economy.db")
            cur = await conn.cursor()

            tableName = str(ctx.guild.id)
            await cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
            result = await cur.fetchone()

            if result is not None:
                await cur.execute(f"""SELECT Balance FROM "{ctx.guild.id}" WHERE UserID =? """,(ctx.author.id,))
                result = await cur.fetchone()

                if result is None:
                    await cur.execute(f"""INSERT INTO "{ctx.guild.id}" (UserID, Balance, Work) VALUES (?,?,?)""",(ctx.author.id, 0.00, 0.00))
                    await conn.commit()
                await cur.execute(f"""SELECT Balance FROM "{ctx.guild.id}" WHERE UserID =? """,(ctx.author.id,))
                balance = await cur.fetchone()
                balance = balance[0]
                print(balance)
                await cur.execute(f"""SELECT Work FROM "{ctx.guild.id}" WHERE UserID =? """,(ctx.author.id,))
                work = await cur.fetchone()
                work = work[0]

                new_work = work + time
                new_balance = balance + total_earnings

                await cur.execute(f"""UPDATE "{ctx.guild.id}" SET Balance = ? , Work = ? WHERE UserID = ?;""",(new_balance, new_work, ctx.author.id))
                await conn.commit()
                await conn.close()

                conn = await aiosqlite.connect('economy.db')
                cur = await conn.cursor()
                
                await cur.execute(f"""SELECT Balance FROM "Global" WHERE UserID =? """,(ctx.author.id,))
                result = await cur.fetchone()

                if result is None:
                    await cur.execute(f"""INSERT INTO "Global" (UserID, Balance, Work) VALUES (?,?,?)""",(ctx.author.id, 0.00, 0.00))
                    await conn.commit()
                await cur.execute(f"""SELECT Balance FROM "Global" WHERE UserID =? """,(ctx.author.id,))
                balance = await cur.fetchone()
                balance = balance[0]

                await cur.execute(f"""SELECT Work FROM "Global" WHERE UserID =? """,(ctx.author.id,))
                work = await cur.fetchone()
                work = work[0]

                new_work = work + time
                new_balance = balance + total_earnings

                await cur.execute(f"""UPDATE "Global" SET Balance = ? , Work = ? WHERE UserID = ?;""",(new_balance, new_work, ctx.author.id))
                await conn.commit()
                await conn.close()

            else:
                await ctx.send("Economy is not enabled here, contact your server administrators")
                self.work.reset_cooldown(ctx)
                return

            await ctx.send(f"💼 You worked {time} hours and earned **${money_per_hour}** per hour.\n"
                       f"💰 Total earnings: **${total_earnings}**\n"
                       f"🏦 New balance: **${new_balance:.2f}**")

    @work.error
    async def work_error(self, ctx, error):
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


    @commands.hybrid_command(name = "baltop")
    async def baltop(self, ctx:commands.Context):
        conn = await aiosqlite.connect("economy.db")
        cur = await conn.cursor()

        tableName = str(ctx.guild.id)
        await cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
        result = await cur.fetchone()
        
        if result is None:
            await ctx.send("Economy not initialized for this server")
        else:
            await cur.execute(f"""SELECT Balance FROM "{ctx.guild.id}" WHERE UserID =? """,(ctx.author.id,))
            result = await cur.fetchone()

            if result is None:
                await cur.execute(f"""INSERT INTO "{ctx.guild.id}" (UserID, Balance, Work) VALUES (?,?,?)""",(ctx.author.id, 0.00, 0.00))
                await conn.commit()
            
            await cur.execute(f"""SELECT UserID, Balance FROM "{ctx.guild.id}" ORDER BY Balance DESC""")
            rows = await cur.fetchall()

            user_ids = [row[0] for row in rows]
            balances = [row[1] for row in rows] 
            sorted_pairs = sorted(zip(balances, user_ids), reverse=True)

            balances, user_ids = zip(*sorted_pairs)

            balances = list(balances)
            user_ids = list(user_ids)
            
            resultant_str = ""
            for i in range(len(balances)):
                resultant_str += f"{i+1}. {(await self.bot.fetch_user(user_ids[i])).name}      ::::      ${balances[i]}\n"
            await conn.close()
            await ctx.send(resultant_str)

    @commands.hybrid_command(name = "baltop-global")
    async def baltopglobal(self, ctx:commands.Context):
        conn = await aiosqlite.connect("economy.db")
        cur = await conn.cursor()

        await cur.execute(f"""SELECT Balance FROM "Global" WHERE UserID =? """,(ctx.author.id,))
        result = await cur.fetchone()

        if result is None:
            await cur.execute(f"""INSERT INTO "{ctx.guild.id}" (UserID, Balance, Work) VALUES (?,?,?)""",(ctx.author.id, 0.00, 0.00))
            await conn.commit()
        
        await cur.execute(f"""SELECT UserID, Balance FROM "Global" ORDER BY Balance DESC""")
        rows = await cur.fetchall()

        user_ids = [row[0] for row in rows]
        balances = [row[1] for row in rows] 
        sorted_pairs = sorted(zip(balances, user_ids), reverse=True)

        balances, user_ids = zip(*sorted_pairs)

        balances = list(balances)
        user_ids = list(user_ids)
        
        resultant_str = ""
        for i in range(len(balances)):
            resultant_str += f"{i+1}. {(await self.bot.fetch_user(user_ids[i])).name}      ::::      ${balances[i]}\n"
        await conn.close()
        await ctx.send(resultant_str)

    @commands.hybrid_command(name = "aboutme")
    async def aboutme(self, ctx:commands.Context):
        conn = await aiosqlite.connect("economy.db")
        cur = await conn.cursor()

        await cur.execute(f"""SELECT Balance FROM "Global" WHERE UserID =? """,(ctx.author.id,))
        result = await cur.fetchone()

        if result is None:
            await cur.execute(f"""INSERT INTO "{ctx.guild.id}" (UserID, Balance, Work) VALUES (?,?,?)""",(ctx.author.id, 0.00, 0.00))
            await conn.commit()
        
        await cur.execute(f"""SELECT Balance FROM "Global" WHERE UserID = ?""",(ctx.author.id,))
        rows = await cur.fetchone()
        rows_global = rows[0]
        msg = f"Money you have globally: {rows_global}\n"
        tableName = str(ctx.guild.id)
        await cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
        result = await cur.fetchone()
        
        if result is None:
            msg += "Economy not initialized for this server"
        else:
            await cur.execute(f"""SELECT Balance FROM "{ctx.guild.id}" WHERE UserID =? """,(ctx.author.id,))
            result = await cur.fetchone()

            if result is None:
                await cur.execute(f"""INSERT INTO "{ctx.guild.id}" (UserID, Balance, Work) VALUES (?,?,?)""",(ctx.author.id, 0.00, 0.00))
                await conn.commit()
            
            await cur.execute(f"""SELECT Balance FROM "{ctx.guild.id}" WHERE UserID = ?""",(ctx.author.id,))
            rows = await cur.fetchone()
            real = rows[0]

            msg += f"Money you have in this server: {real}"

            await ctx.send(msg)

        

    
async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))