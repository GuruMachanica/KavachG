const { sequelize } = require('../config/database');
const User = require('./userModel-sqlite');
const Incident = require('./incidentModel-sqlite');

// Define additional relationships if needed
// ...

// Function to sync all models with the database
const syncModels = async (force = false) => {
  try {
    await sequelize.sync({ force });
    console.log('All models were synchronized successfully.');
    return true;
  } catch (error) {
    console.error('Error synchronizing models:', error);
    return false;
  }
};

// Create initial admin user
const createInitialAdmin = async () => {
  try {
    // Check if admin exists
    const adminCount = await User.count({ where: { role: 'admin' } });
    
    if (adminCount === 0) {
      // Create admin user
      await User.create({
        name: 'Admin',
        email: 'admin@12.com',
        password: 'admin123456',
        role: 'admin'
      });
      console.log('Initial admin user created');
    } else {
      console.log('Admin user already exists');
    }
  } catch (error) {
    console.error('Error creating initial admin user:', error);
  }
};

module.exports = {
  sequelize,
  User,
  Incident,
  syncModels,
  createInitialAdmin
}; 