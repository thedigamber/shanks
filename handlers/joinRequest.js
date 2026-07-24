const { GROUP_ID } = require('../config');

module.exports = async (ctx) => {
  // ctx.update.chat_join_request contains the request
  const request = ctx.update.chat_join_request;
  if (!request) return;

  // Only process requests for our group
  if (request.chat.id !== GROUP_ID) return;

  const userId = request.from.id;

  try {
    await ctx.approveChatJoinRequest(GROUP_ID, userId);
    console.log(`✅ Auto‑approved join request from ${userId}`);
  } catch (err) {
    console.error(`❌ Failed to approve ${userId}:`, err.message);
  }
};
