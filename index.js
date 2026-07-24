const { Telegraf } = require('telegraf');
const { BOT_TOKEN } = require('./config');

// Import handlers
const startHandler = require('./handlers/start');
const joinRequestHandler = require('./handlers/joinRequest');

const bot = new Telegraf(BOT_TOKEN);

// Auto‑approve join requests
bot.on('chat_join_request', joinRequestHandler);

// /start command (only in DM)
bot.command('start', startHandler);

// Start polling
bot.launch()
  .then(() => console.log('🤖 Bot is running...'))
  .catch(err => console.error('❌ Launch error:', err));

// Graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
