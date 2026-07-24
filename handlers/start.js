const { Markup } = require('telegraf');
const { GROUP_ID, GROUP_INVITE_LINK } = require('../config');
const { isUserInGroup } = require('../utils');

module.exports = async (ctx) => {
  // Only respond to private chats
  if (ctx.chat.type !== 'private') return;

  const userId = ctx.from.id;

  // Check membership
  const inGroup = await isUserInGroup(ctx.bot, userId);
  console.log(`User ${userId} inGroup: ${inGroup}`);

  if (inGroup) {
    // User is a member – now you can give them the content (APK, etc.)
    await ctx.reply(
      '✅ You are a member of the group!\n' +
      'Here is your content:\n' +
      '(Replace this with your APK link or file)'
    );
  } else {
    // Not a member → ask to join
    await ctx.reply(
      '🚫 You must join our private group first to access the content.\n' +
      'Please click the button below to join, then send /start again.',
      Markup.inlineKeyboard([
        Markup.button.url('🔗 Join Group', GROUP_INVITE_LINK)
      ])
    );
  }
};
