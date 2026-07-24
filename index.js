const { Telegraf } = require('telegraf');
const { BOT_TOKEN } = require('./config');

// Import handlers
const startHandler = require('./handlers/start');
const joinRequestHandler = require('./handlers/joinRequest');

// Start HTTP server (to satisfy Render port requirement)
require('./server');

// Create bot instance
const bot = new Telegraf(BOT_TOKEN);

// Auto‑approve join requests
bot.on('chat_join_request', joinRequestHandler);

// /start command
bot.command('start', startHandler);

// Launch bot (long polling)
bot.launch()
  .then(() => console.log('🤖 Bot started successfully'))
  .catch(err => console.error('❌ Bot launch error:', err));

// Graceful shutdown
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
