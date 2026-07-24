const { GROUP_ID } = require('./config');

async function isUserInGroup(bot, userId) {
  try {
    const member = await bot.telegram.getChatMember(GROUP_ID, userId);
    // status: 'member', 'administrator', 'creator' → in group
    return !['left', 'kicked'].includes(member.status);
  } catch (error) {
    return false;
  }
}

module.exports = { isUserInGroup };
