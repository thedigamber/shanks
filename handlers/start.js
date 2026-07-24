const { Markup } = require('telegraf');
const { GROUP_ID, GROUP_INVITE_LINK } = require('../config');
const { isUserInGroup } = require('../utils');

module.exports = async (ctx) => {
  // Only respond in private chats
  if (ctx.chat.type !== 'private') return;

  const userId = ctx.from.id;

  const inGroup = await isUserInGroup(ctx.bot, userId);

  if (inGroup) {
    await ctx.reply(
      '✅ आप group के member हैं! अब आप bot का इस्तेमाल कर सकते हैं।\n' +
      '(यहाँ आप अपनी अगली commands जोड़ सकते हैं)'
    );
  } else {
    await ctx.reply(
      '🚫 आपको पहले हमारे private group में join होना होगा।\n' +
      'नीचे दिए गए button पर क्लिक करें, join करें, फिर /start दोबारा भेजें।',
      Markup.inlineKeyboard([
        Markup.button.url('🔗 Group Join करें', GROUP_INVITE_LINK)
      ])
    );
  }
};
