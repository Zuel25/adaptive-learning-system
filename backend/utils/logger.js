const fs = require('fs');
const path = require('path');

const logDir = path.join(__dirname, '../logs');

// Create logs directory if not exists
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3
};

const currentLogLevel = logLevels[process.env.LOG_LEVEL || 'info'];

const log = (level, message, data = {}) => {
  if (logLevels[level] > currentLogLevel) return;

  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  const logEntry = `${logMessage} ${JSON.stringify(data)}\n`;

  // Log ke console
  console.log(logMessage, data);

  // Log ke file
  const logFile = path.join(logDir, `${level}.log`);
  fs.appendFileSync(logFile, logEntry);
};

module.exports = {
  error: (message, data) => log('error', message, data),
  warn: (message, data) => log('warn', message, data),
  info: (message, data) => log('info', message, data),
  debug: (message, data) => log('debug', message, data)
};