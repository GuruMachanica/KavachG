require('dotenv').config();
const path = require('path');

module.exports = {
  PORT: process.env.PORT || 5000,
  MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/safety_monitoring',
  JWT_SECRET: process.env.JWT_SECRET || 'kavachg_safety_jwt_secret_key',
  NODE_ENV: process.env.NODE_ENV || 'development'
}; 