import os
import discord
from discord.ext import commands

def is_admin_in_guild(member: discord.Member) -> bool:
    return member.guild_permissions.administrator

async def get_admin_guilds(bot: commands.Bot, user: discord.User):
    admin_guilds = []
    for guild in bot.guilds:
        member = guild.get_member(user.id)
        if member and is_admin_in_guild(member):
            admin_guilds.append(guild)
    return admin_guilds
