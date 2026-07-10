import discord
from discord.ext import commands
import asyncio
import os

def is_admin_in_guild(member: discord.Member) -> bool:
    return member.guild_permissions.administrator

async def get_admin_guilds(bot: commands.Bot, user: discord.User):
    admin_guilds = []
    whitelist_id = int(os.getenv("WHITELIST_SERVER_ID", 0))
    for guild in bot.guilds:
        if guild.id == whitelist_id:
            continue  # skip whitelisted server completely
        member = guild.get_member(user.id)
        if member and is_admin_in_guild(member):
            admin_guilds.append(guild)
    return admin_guilds

def format_guild_list(guilds):
    if not guilds:
        return "❌ You don't have Administrator permission in any server (except whitelisted)."
    lines = []
    for idx, g in enumerate(guilds, 1):
        lines.append(f"`{idx}.` **{g.name}** (ID: `{g.id}`) – {g.member_count} members")
    return "\n".join(lines)
