require('dotenv').config();

module.exports = {
  BOT_TOKEN: process.env.BOT_TOKEN,
  GROUP_ID: parseInt(process.env.GROUP_ID),   // integer
  GROUP_INVITE_LINK: process.env.GROUP_INVITE_LINK
};
