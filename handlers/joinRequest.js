const { GROUP_ID } = require('../config');

module.exports = async (ctx) => {
  const request = ctx.update.chat_join_request;
  if (!request) return;
  if (request.chat.id !== GROUP_ID) return;

  const userId = request.from.id;
  try {
    await ctx.approveChatJoinRequest(GROUP_ID, userId);
    console.log(`✅ Approved join request from ${userId}`);
  } catch (err) {
    console.error(`❌ Failed to approve ${userId}:`, err.message);
  }
};
