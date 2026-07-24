const { GROUP_ID } = require('./config');

async function isUserInGroup(bot, userId) {
  try {
    const member = await bot.telegram.getChatMember(GROUP_ID, userId);
    // 'creator', 'administrator', 'member' → in group
    const allowed = ['creator', 'administrator', 'member'];
    return allowed.includes(member.status);
  } catch (error) {
    // If error (e.g., user not found), they are not in group
    console.log(`Membership check error for ${userId}: ${error.description || error.message}`);
    return false;
  }
}

module.exports = { isUserInGroup };
