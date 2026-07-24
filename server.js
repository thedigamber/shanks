const express = require('express');
const { PORT } = require('./config');

const app = express();

app.get('/', (req, res) => {
  res.send('Bot is running!');
});

app.listen(PORT, () => {
  console.log(`🌐 HTTP server listening on port ${PORT}`);
});
