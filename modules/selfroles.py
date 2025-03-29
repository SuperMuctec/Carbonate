import discord
from discord.ext import commands
import sqlite3


class SelfRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You have missing permissions [Administrator]")
    
    @commands.hybrid_command(name="addselfassignablerole")
    @commands.has_permissions(administrator=True)
    @discord.app_commands.describe(
        role="The Role"
    )
    async def set_rules(self,
        ctx: commands.Context,
        role: discord.Role,
    ):
        srver = ctx.guild.id
        role = role.id
        conn = sqlite3.connect('self-roles.db')
        cur = conn.cursor()

        if int(srver) == ctx.guild.id:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS '{str(srver)}' (
                    name TEXT,
                    id TEXT
                );
            """)
            cur.execute(f"SELECT id FROM '{str(srver)}'")
            roleids = [row[0] for row in cur.fetchall()]

            cur.execute(f"SELECT name FROM '{str(srver)}'")
            rolenames = [row[0] for row in cur.fetchall()]
            
            if str(role) not in roleids:
                if ctx.guild.get_role(int(role)) != None:
                    cur.execute(f'INSERT INTO "{str(srver)}" (name, id) VALUES (?, ?)', (ctx.guild.get_role(int(role)).name, role))
                    conn.commit()
                    conn.close() 
                    await ctx.send(f"Added New Self assignable role of id {role} and name {ctx.guild.get_role(int(role)).name} initialized")
                else:
                    await ctx.send("Role does not exist")
            else:
                await ctx.send("This role is already listed, do ```/selfroles``` for all the listed self roles")


    @commands.hybrid_command(name = "removeselfassignablerole")
    @commands.has_permissions(administrator = True)
    @discord.app_commands.describe(role = "The role you want to remove")
    async def remove_self_assignable_role(self, ctx:commands.Context, role: discord.Role):
        srver = ctx.guild.id
        role = role.id
        conn = sqlite3.connect('self-roles.db')
        cur = conn.cursor()
        

        if int(srver) == ctx.guild.id:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS "{str(srver)}" (
                    name TEXT,
                    id TEXT
                );
            """)
            cur.execute(f"SELECT id FROM '{str(srver)}'")
            roleids = [row[0] for row in cur.fetchall()]

            cur.execute(f"SELECT name FROM '{str(srver)}'")
            rolenames = [row[0] for row in cur.fetchall()]
            print(roleids)
            if str(role) in roleids:
                if ctx.guild.get_role(int(role)) != None:
                    cur.execute(f'DELETE FROM "{str(srver)}" WHERE id = ?', (role,))
                    conn.commit()
                    conn.close() 
                    await ctx.send(f"Removed Self assignable role of id {role} and name {ctx.guild.get_role(int(role)).name} removed")
                else:
                    await ctx.send("Role Does not exist")
            else:
                await ctx.send("This role is not listed, do ```/selfroles``` for all the listed self roles")
    
    @commands.hybrid_command(name="selfroles")
    async def list_self_roles(self, ctx: commands.Context):
        conn = sqlite3.connect('self-roles.db')
        cur = conn.cursor()
        srver = ctx.guild.id

        # Send a "Processing..." message first
        message = await ctx.send("Processing self-assignable roles...")

        # Check if table exists
        listOfTables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (str(srver),)
        ).fetchall()

        if listOfTables:
            cur.execute(f"SELECT id FROM '{srver}'")
            roleids = [row[0] for row in cur.fetchall()]

            cur.execute(f"SELECT name FROM '{srver}'")
            rolenames = [row[0] for row in cur.fetchall()]

            embed = discord.Embed(
                title="👋 The self-assignable roles in this server are!",
                description="Use `!giverole help` for more details.",
                color=discord.Color.random(),
            )

            crect = 0  # Role count tracker
            for i, role_id in enumerate(roleids):
                if role_id:
                    embed.add_field(
                        name=f"Role {i+1}, ID: {role_id}",
                        value=f"Role Name: {rolenames[i]}",
                        inline=False
                    )
                    crect += 1

            if crect == 0:
                embed.add_field(name="No Roles", value="There are no self-assignable roles.", inline=False)

            embed.set_footer(text="Let me know if you need any more help at supermutec 🚀")

            # Edit the original "Processing..." message with the embed
            await message.edit(content="", embed=embed)
        else:
            await message.edit(content="❌ No self-assignable roles set for this server. Contact an admin.")

        conn.close()

    @commands.hybrid_command(name="giverole")
    @discord.app_commands.describe(role="The role you want")
    async def give_role(self, ctx: commands.Context, role: discord.Role):
        srver = ctx.guild.id

        # For hybrid commands, use interaction defer to avoid timeout
        await ctx.defer()

        # Connect to SQLite
        conn = sqlite3.connect("self-roles.db")
        cur = conn.cursor()

        # Check if the server has self-assignable roles
        cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (str(srver),))
        table_exists = cur.fetchone()[0]

        if not table_exists:
            await ctx.reply("❌ This server does not have self-assignable roles set up.")
            conn.close()
            return

        # Check if role exists in database
        cur.execute(f"SELECT id FROM '{srver}' WHERE id=?", (str(role.id),))
        role_exists = cur.fetchone()

        conn.close()

        if role_exists:
            try:
                await ctx.author.add_roles(role)
                await ctx.reply(f"✅ Assigned role **{role.name}** to {ctx.author.mention}.")
            except discord.Forbidden:
                await ctx.reply("❌ I do not have permission to manage roles.")
            except Exception as e:
                await ctx.reply(f"⚠️ Error: {e}")
        else:
            await ctx.reply("❌ That role is **not self-assignable**. Use `/selfroles` to see available roles.")
    
    @commands.hybrid_command(name = "roleid")
    @discord.app_commands.describe(role = "The role whose id you want to find")
    async def roleid(self, ctx:commands.Context, role: discord.Role):
        await ctx.defer()
        role_name = role.name
        
        if role:
            await ctx.send(f"Role ID -> `{role.id}` \nRole name -> {role_name}")
        else:
            await message.channel.send("Role not found!")

    @commands.hybrid_command(name = "list-roles")
    async def getroles(self, ctx: commands.Context):
        embed = discord.Embed(
                title="👋 The self assignable roles in this server are!",
                description="The self assignable roles in this server, use ```!giverole help``` for more",
                color=discord.Color.random()
        )
        count = 0
        crect = 0
        roles = ctx.guild.roles 
        roleids = []
        rolenames = []
        for rohle in roles:
            roleids.append(rohle.id)
            rolenames.append(rohle.name)
        for i in range(len(roleids)):
            if rolenames[i] == '@everyone':
                count += 1
            elif roleids[i] != '':
                embed.add_field(name=f"Role {i+1 - count}, Id: {roleids[i]}", inline=False, value=f"Role name: {rolenames[i]} \n Role id: {roleids[i]}")
                crect += 1
            else:
                count += 1

        if crect == 0:
            embed.add_field(name=f"No Role", inline=False, value=f"There are no self assignable roles in this server")

        embed.set_footer(text="Let me know if you need any more help at supermutec 🚀")

        await ctx.send(embed=embed)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(SelfRoles(bot))
