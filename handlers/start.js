const { Markup } = require('telegraf');
const { GROUP_ID, GROUP_INVITE_LINK } = require('../config');
const { isUserInGroup } = require('../utils');

module.exports = async (ctx) => {
  if (ctx.chat.type !== 'private') return;

  const userId = ctx.from.id;
  const inGroup = await isUserInGroup(ctx.telegram, userId);   // ✅ pass ctx.telegram

  console.log(`User ${userId} inGroup: ${inGroup}`);

  if (inGroup) {
    await ctx.reply(
      '✅ You are a member of the group!\n' +
      'Here is your content:\n' +
      '(Replace this with your APK link or file)'
    );
  } else {
    await ctx.reply(
      '🚫 You must join our private group first to access the content.\n' +
      'Please click the button below to join, then send /start again.',
      Markup.inlineKeyboard([
        Markup.button.url('🔗 Join Group', GROUP_INVITE_LINK)
      ])
    );
  }
};
