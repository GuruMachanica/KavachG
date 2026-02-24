const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

// Import SQLite database models and connection
const { sequelize, syncModels, createInitialAdmin } = require('./models');
const { testConnection } = require('./config/database');

// Import routes
const incidentRoutes = require('./routes/incidentRoutes-sqlite');
const userRoutes = require('./routes/userRoutes-sqlite');

// Create Express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Define routes
app.use('/api/incidents', incidentRoutes);
app.use('/api/users', userRoutes);

// Health check route
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'OK', message: 'Server is running with SQLite' });
});

// App initialization
const PORT = process.env.PORT || 5000;

// Initialize database and start server
const initializeApp = async () => {
  try {
    // Test database connection
    const dbConnected = await testConnection();
    
    if (!dbConnected) {
      console.error('Failed to connect to SQLite database. Exiting...');
      process.exit(1);
    }
    
    // Sync all models with the database
    console.log('Syncing database models...');
    await syncModels(true); // Force: true to recreate tables and ensure all tables exist
    
    // Create initial admin user if none exists
    await createInitialAdmin();
    
    // Start the server
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Error during app initialization:', error);
    process.exit(1);
  }
};

// Start the application
initializeApp(); 