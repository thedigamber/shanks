require('dotenv').config();

module.exports = {
  BOT_TOKEN: process.env.BOT_TOKEN,
  GROUP_ID: parseInt(process.env.GROUP_ID, 10),
  GROUP_INVITE_LINK: process.env.GROUP_INVITE_LINK,
  PORT: parseInt(process.env.PORT, 10) || 3000
};
