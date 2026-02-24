const { Sequelize } = require('sequelize');
const path = require('path');

// Create SQLite database connection
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: path.join(__dirname, '../../safety_monitoring.sqlite'),
  logging: false // Set to console.log to see SQL queries
});

// Test the connection
const testConnection = async () => {
  try {
    await sequelize.authenticate();
    console.log('SQLite database connection has been established successfully.');
    return true;
  } catch (error) {
    console.error('Unable to connect to the SQLite database:', error);
    return false;
  }
};

module.exports = {
  sequelize,
  testConnection
}; 