const { Telegraf } = require('telegraf');
const { BOT_TOKEN } = require('./config');
const startHandler = require('./handlers/start');
const joinRequestHandler = require('./handlers/joinRequest');

require('./server');  // keep HTTP server for Render

const bot = new Telegraf(BOT_TOKEN);

bot.on('chat_join_request', joinRequestHandler);
bot.command('start', startHandler);

bot.launch()
  .then(() => console.log('🤖 Bot started successfully'))
  .catch(err => console.error('❌ Bot launch error:', err));

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
