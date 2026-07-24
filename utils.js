const { GROUP_ID } = require('./config');

async function isUserInGroup(telegram, userId) {
  try {
    const member = await telegram.getChatMember(GROUP_ID, userId);
    const allowed = ['creator', 'administrator', 'member'];
    return allowed.includes(member.status);
  } catch (error) {
    console.log(`Membership check error for ${userId}: ${error.description || error.message}`);
    return false;
  }
}

module.exports = { isUserInGroup };
